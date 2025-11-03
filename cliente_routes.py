from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from main import limiter
from schemas import (
    ClienteCompletoSchema, ContratoDetalhadoSchema, ContratosResponseSchema
)
from models import Contrato, Endereco, Usuario, Cliente, Financeiro
from main import bcrypt_context
from datetime import date

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
        session.begin()
        
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
