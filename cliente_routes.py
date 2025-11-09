from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from main import limiter
from schemas import (
    ClienteCompletoSchema, ContratoDetalhadoSchema, ContratosResponseSchema,
    SolicitacaoCompletaSchema, ContratoCompletoSchema, VeiculoCompletoSchema,
    FinanceiroCompletoSchema, ParcelaSchema
)
from models import Contrato, Endereco, Usuario, Cliente, Financeiro, Veiculo, Parcela
from main import bcrypt_context
from datetime import date, timedelta
from calendar import monthrange
import re

cliente_router = APIRouter(prefix="/cliente", tags=["cliente"])


@cliente_router.post("/cadastro-completo")
@limiter.limit("3/minute")  
async def cadastrar_cliente_completo(
    request: Request,
    dados: ClienteCompletoSchema,
    session: Session = Depends(pegar_sessao)
):
    """
    Cadastra cliente completo (endereço + usuário + cliente) em uma única transação
    """
    try:
        usuario_existente = session.query(Usuario).filter(Usuario.login == dados.login).first()
        if usuario_existente:
            session.rollback()
            raise HTTPException(status_code=400, detail="Login já cadastrado")
        
        cliente_existente = session.query(Cliente).filter(Cliente.cpf == dados.cpf).first()
        if cliente_existente:
            session.rollback()
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
        
        email_existente = session.query(Cliente).filter(Cliente.email == dados.email).first()
        if email_existente:
            session.rollback()
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        endereco = Endereco(
            logradouro=dados.logradouro,
            numero=dados.numero,
            bairro=dados.bairro,
            cidade=dados.cidade,
            estado=dados.estado,
            cep=dados.cep
        )
        session.add(endereco)
        session.flush() 
        
        import bcrypt
        senha_bytes = dados.senha.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode('utf-8')
        
        usuario = Usuario(
            id_perfil=dados.id_perfil,
            login=dados.login,
            senha_hash=senha_hash,
            data_criacao=date.today()
        )
        session.add(usuario)
        session.flush()  
        
        cliente = Cliente(
            id_usuario=usuario.id_usuario,
            id_endereco=endereco.id_endereco,
            nome=dados.nome,
            cpf=dados.cpf,
            email=dados.email,
            telefone=dados.telefone,
            renda=dados.renda,
            data_cadastro=date.today()
        )
        session.add(cliente)
        
        session.commit()
        
        return {
            "success": True, 
            "id_cliente": cliente.id_cliente,
            "id_usuario": usuario.id_usuario,
            "id_endereco": endereco.id_endereco,
            "message": "Cliente cadastrado com sucesso"
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()  
        raise HTTPException(status_code=400, detail=f"Erro no cadastro completo: {str(e)}")


@cliente_router.get("/contratos/{id_cliente}", response_model=ContratosResponseSchema, dependencies=[Depends(verificar_token)])
async def contratos(id_cliente: int, session: Session = Depends(pegar_sessao)):
    """
    Retorna informações detalhadas de TODOS os contratos do cliente:
    - Número do Contrato
    - Status
    - ID Cliente
    - ID Veículo
    - ID Financeiro
    - Data Emissão
    """
    contratos = session.query(Contrato).filter(Contrato.id_cliente == id_cliente).all()
    
    if not contratos:
        raise HTTPException(status_code=404, detail="Nenhum contrato encontrado para este cliente")
    
    contratos_detalhados = []
    
    for contrato in contratos:
        financeiro = session.query(Financeiro).filter(Financeiro.id_contrato == contrato.id_contrato).first()
        
        if financeiro:  
            contrato_detalhado = ContratoDetalhadoSchema(
                id_contrato=contrato.id_contrato,
                numero_contrato=contrato.num_contrato,
                status=contrato.status,
                id_cliente=contrato.id_cliente,
                id_veiculo=contrato.id_veiculo,
                id_financeiro=financeiro.id_financeiro,
                data_emissao=contrato.data_emissao
            )
            contratos_detalhados.append(contrato_detalhado)
    
    if not contratos_detalhados:
        raise HTTPException(status_code=404, detail="Nenhum contrato com dados financeiros encontrado para este cliente")
    
    return ContratosResponseSchema(
        contratos=contratos_detalhados,
        total=len(contratos_detalhados)
    )


@cliente_router.get("/contrato/{id_contrato}", response_model=ContratoCompletoSchema, dependencies=[Depends(verificar_token)])
async def detalhes_contrato(id_contrato: int, session: Session = Depends(pegar_sessao)):
    """
    Retorna informações completas de um contrato específico:
    - Dados do Contrato
    - Dados do Veículo
    - Dados Financeiros
    - Todas as Parcelas
    """
    contrato = session.query(Contrato).filter(Contrato.id_contrato == id_contrato).first()
    
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    veiculo = session.query(Veiculo).filter(Veiculo.id_veiculo == contrato.id_veiculo).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado para este contrato")
    
    financeiro = session.query(Financeiro).filter(Financeiro.id_contrato == contrato.id_contrato).first()
    if not financeiro:
        raise HTTPException(status_code=404, detail="Dados financeiros não encontrados para este contrato")
    
    parcelas = session.query(Parcela).filter(Parcela.id_financeiro == financeiro.id_financeiro).order_by(Parcela.numero_parcela).all()
    
    parcelas_schema = [
        ParcelaSchema(
            id_parcela=p.id_parcela,
            numero_parcela=p.numero_parcela,
            valor_parcela=float(p.valor_parcela),
            data_vencimento=p.data_vencimento,
            data_pagamento=p.data_pagamento,
            valor_pago=float(p.valor_pago) if p.valor_pago else None,
            status=p.status
        ) for p in parcelas
    ]
    
    financeiro_schema = FinanceiroCompletoSchema(
        id_financeiro=financeiro.id_financeiro,
        valor_total=float(financeiro.valor_total),
        valor_entrada=float(financeiro.valor_entrada),
        taxa_juros=float(financeiro.taxa_juros) if financeiro.taxa_juros else None,
        qtde_parcelas=financeiro.qtde_parcelas,
        data_primeiro_vencimento=financeiro.data_primeiro_vencimento,
        status_pagamento=financeiro.status_pagamento,
        data_criacao=financeiro.data_criacao,
        parcelas=parcelas_schema
    )
    
    veiculo_schema = VeiculoCompletoSchema(
        id_veiculo=veiculo.id_veiculo,
        marca=veiculo.marca,
        modelo=veiculo.modelo,
        ano_fabricacao=veiculo.ano_fabricacao,
        ano_modelo=veiculo.ano_modelo,
        cor=veiculo.cor,
        placa=veiculo.placa,
        num_chassi=veiculo.num_chassi,
        num_renavam=veiculo.num_renavam,
        valor=float(veiculo.valor)
    )
    
    return ContratoCompletoSchema(
        id_contrato=contrato.id_contrato,
        numero_contrato=contrato.num_contrato,
        status=contrato.status,
        id_cliente=contrato.id_cliente,
        data_emissao=contrato.data_emissao,
        vigencia_fim=contrato.vigencia_fim,
        veiculo=veiculo_schema,
        financeiro=financeiro_schema
    )


def gerar_numero_contrato(session: Session) -> str:
    """
    Gera um número de contrato único no formato: CT-YYYYMMDD-XXXX
    """
    hoje = date.today()
    prefixo = f"CT-{hoje.strftime('%Y%m%d')}"
    
    # Busca o último contrato do dia
    ultimo_contrato = session.query(Contrato).filter(
        Contrato.num_contrato.like(f"{prefixo}-%")
    ).order_by(Contrato.num_contrato.desc()).first()
    
    if ultimo_contrato:
        # Extrai o número sequencial e incrementa
        ultimo_numero = int(ultimo_contrato.num_contrato.split('-')[-1])
        novo_numero = ultimo_numero + 1
    else:
        novo_numero = 1
    
    return f"{prefixo}-{novo_numero:04d}"


def extrair_ano_do_codigo_fipe(ano_codigo: str) -> tuple[int, int]:
    """
    Extrai ano de fabricação e ano modelo do código FIPE.
    O código FIPE geralmente vem como "2024-1" ou "2024" ou apenas o ano.
    Retorna (ano_fabricacao, ano_modelo)
    """
    if not ano_codigo:
        raise ValueError("Código do ano não fornecido")

    match = re.search(r'(\d{4})', str(ano_codigo))
    if match:
        ano = int(match.group(1))

        return (ano, ano)
    
    raise ValueError(f"Não foi possível extrair o ano do código: {ano_codigo}")


@cliente_router.post("/solicitacao", dependencies=[Depends(verificar_token)])
@limiter.limit("5/minute")
async def criar_solicitacao_financiamento(
    request: Request,
    dados: SolicitacaoCompletaSchema,
    session: Session = Depends(pegar_sessao)
):
    """
    Cria uma solicitação de financiamento completa:
    - Cria o Veículo
    - Cria o Contrato
    - Cria o Financeiro
    - Cria todas as Parcelas
    """
    try:
        cliente = session.query(Cliente).filter(Cliente.id_cliente == dados.id_cliente).first()
        if not cliente:
            session.rollback()
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        placa_normalizada = dados.veiculo.placa.upper().replace('-', '').replace(' ', '')
        chassi_normalizado = dados.veiculo.numChassi.upper().strip()
        renavam_normalizado = dados.veiculo.numRenavam.strip()
        
        veiculo_existente_placa = session.query(Veiculo).filter(
            Veiculo.placa == placa_normalizada
        ).first()
        if veiculo_existente_placa:
            session.rollback()
            raise HTTPException(status_code=400, detail="Placa já cadastrada")
        
        veiculo_existente_chassi = session.query(Veiculo).filter(
            Veiculo.num_chassi == chassi_normalizado
        ).first()
        if veiculo_existente_chassi:
            session.rollback()
            raise HTTPException(status_code=400, detail="Chassi já cadastrado")
        
        veiculo_existente_renavam = session.query(Veiculo).filter(
            Veiculo.num_renavam == renavam_normalizado
        ).first()
        if veiculo_existente_renavam:
            session.rollback()
            raise HTTPException(status_code=400, detail="RENAVAM já cadastrado")
        
        try:
            ano_fabricacao, ano_modelo = extrair_ano_do_codigo_fipe(dados.anoSelecionado)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"Erro ao processar ano: {str(e)}")
        
        veiculo = Veiculo(
            marca=dados.marcaNome or "Não informado",
            modelo=dados.modeloNome or "Não informado",
            ano_fabricacao=ano_fabricacao,
            ano_modelo=ano_modelo,
            cor=dados.veiculo.cor,
            placa=placa_normalizada,
            num_chassi=chassi_normalizado,
            num_renavam=renavam_normalizado,
            valor=float(dados.financeiro.valorVeiculo)
        )
        session.add(veiculo)
        session.flush()
        
        num_contrato = gerar_numero_contrato(session)
        
        data_emissao = date.today()
        data_primeiro_vencimento = data_emissao + timedelta(days=30)
        
        contrato = Contrato(
            id_cliente=dados.id_cliente,
            id_veiculo=veiculo.id_veiculo,
            num_contrato=num_contrato,
            data_emissao=data_emissao,
            status="pendente"  # Status inicial: pendente de aprovação
        )
        session.add(contrato)
        session.flush()
        
        valor_total = float(dados.financeiro.totalPagar or dados.financeiro.valorVeiculo)
        financeiro = Financeiro(
            id_contrato=contrato.id_contrato,
            valor_total=valor_total,
            valor_entrada=float(dados.financeiro.valorEntrada),
            taxa_juros=float(dados.financeiro.taxaJuros),
            qtde_parcelas=int(dados.financeiro.parcelasSelecionadas),
            data_primeiro_vencimento=data_primeiro_vencimento,
            status_pagamento="em_dia",
            data_criacao=data_emissao
        )
        session.add(financeiro)
        session.flush()
        
        valor_parcela = float(dados.financeiro.valorParcela or (valor_total / dados.financeiro.parcelasSelecionadas))
        qtde_parcelas = int(dados.financeiro.parcelasSelecionadas)
        
        for i in range(1, qtde_parcelas + 1):
            meses_apos_primeiro = i - 1
            if meses_apos_primeiro == 0:
                data_vencimento = data_primeiro_vencimento
            else:
                ano = data_primeiro_vencimento.year
                mes = data_primeiro_vencimento.month
                dia = data_primeiro_vencimento.day
                
                mes += meses_apos_primeiro
                while mes > 12:
                    mes -= 12
                    ano += 1
                
                ultimo_dia_mes = monthrange(ano, mes)[1]
                dia_ajustado = min(dia, ultimo_dia_mes)
                
                data_vencimento = date(ano, mes, dia_ajustado)
            
            parcela = Parcela(
                id_financeiro=financeiro.id_financeiro,
                numero_parcela=i,
                valor_parcela=valor_parcela,
                data_vencimento=data_vencimento,
                status="pendente"
            )
            session.add(parcela)
        
        session.commit()
        
        return {
            "success": True,
            "message": "Solicitação de financiamento criada com sucesso",
            "id_contrato": contrato.id_contrato,
            "id_veiculo": veiculo.id_veiculo,
            "id_financeiro": financeiro.id_financeiro,
            "numero_contrato": num_contrato,
            "total_parcelas": qtde_parcelas
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar solicitação: {str(e)}")
