from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional
from dependencies import pegar_sessao, verificar_token
from models import Contrato, Cliente, Veiculo, Financeiro, Parcela
from schemas import (
    SolicitacoesResponseSchema, SolicitacaoListaSchema, SolicitacaoDetalheSchema,
    ContratosVigentesResponseSchema, ContratoListaSchema, ContratoCompletoSchema,
    VeiculoCompletoSchema, FinanceiroCompletoSchema, ParcelaSchema, AprovarRejeitarSchema,
    ClienteInfoSchema, DashboardMetricasSchema
)
from datetime import date

admin_router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verificar_token)])


@admin_router.get("/dashboard/metrics", response_model=DashboardMetricasSchema)
async def obter_metricas_dashboard(session: Session = Depends(pegar_sessao)):
    """
    Retorna métricas para o dashboard do admin:
    - Solicitações pendentes
    - Contratos ativos
    - Valor total financiado
    - Parcelas em atraso (quantidade e valor)
    """
    from sqlalchemy import func
    from datetime import date
    
    # Solicitações pendentes
    solicitacoes_pendentes = session.query(Contrato).filter(Contrato.status == "pendente").count()
    
    # Contratos ativos
    contratos_ativos = session.query(Contrato).filter(Contrato.status == "ativo").count()
    
    # Valor total financiado (soma de todos os financeiros de contratos ativos)
    valor_total_financiado = session.query(func.sum(Financeiro.valor_total)).join(
        Contrato, Financeiro.id_contrato == Contrato.id_contrato
    ).filter(Contrato.status == "ativo").scalar() or 0.0
    
    # Parcelas em atraso
    hoje = date.today()
    parcelas_em_atraso = session.query(Parcela).join(
        Financeiro, Parcela.id_financeiro == Financeiro.id_financeiro
    ).join(
        Contrato, Financeiro.id_contrato == Contrato.id_contrato
    ).filter(
        Contrato.status == "ativo"
    ).filter(
        (Parcela.status == "atrasada") | 
        ((Parcela.status == "pendente") & (Parcela.data_vencimento < hoje))
    ).all()
    
    parcelas_em_atraso_qtd = len(parcelas_em_atraso)
    parcelas_em_atraso_valor = sum(float(p.valor_parcela) for p in parcelas_em_atraso)
    
    return DashboardMetricasSchema(
        solicitacoes_pendentes=solicitacoes_pendentes,
        contratos_ativos=contratos_ativos,
        valor_total_financiado=float(valor_total_financiado),
        parcelas_em_atraso_qtd=parcelas_em_atraso_qtd,
        parcelas_em_atraso_valor=parcelas_em_atraso_valor
    )


@admin_router.get("/solicitacoes", response_model=SolicitacoesResponseSchema)
async def listar_solicitacoes_abertas(session: Session = Depends(pegar_sessao)):
    """
    Lista todas as solicitações em aberto (contratos com status 'pendente')
    Retorna informações resumidas para o painel admin
    """
    contratos_pendentes = session.query(Contrato).filter(Contrato.status == "pendente").all()
    
    solicitacoes = []
    for contrato in contratos_pendentes:
        cliente = session.query(Cliente).filter(Cliente.id_cliente == contrato.id_cliente).first()
        if not cliente:
            continue
        
        veiculo = session.query(Veiculo).filter(Veiculo.id_veiculo == contrato.id_veiculo).first()
        if not veiculo:
            continue
        
        financeiro = session.query(Financeiro).filter(Financeiro.id_contrato == contrato.id_contrato).first()
        if not financeiro:
            continue
        
        solicitacao = SolicitacaoListaSchema(
            id_contrato=contrato.id_contrato,
            numero_contrato=contrato.num_contrato,
            id_cliente=contrato.id_cliente,
            nome_cliente=cliente.nome,
            marca_veiculo=veiculo.marca,
            modelo_veiculo=veiculo.modelo,
            valor_veiculo=float(veiculo.valor),
            valor_entrada=float(financeiro.valor_entrada),
            qtde_parcelas=financeiro.qtde_parcelas,
            status=contrato.status,
            data_emissao=contrato.data_emissao
        )
        solicitacoes.append(solicitacao)
    
    return SolicitacoesResponseSchema(
        solicitacoes=solicitacoes,
        total=len(solicitacoes)
    )


@admin_router.get("/solicitacao/{id_contrato}", response_model=SolicitacaoDetalheSchema)
async def detalhes_solicitacao(id_contrato: int, session: Session = Depends(pegar_sessao)):
    """
    Retorna detalhes completos de uma solicitação específica
    Inclui dados do cliente, veículo e financeiro
    """
    contrato = session.query(Contrato).filter(Contrato.id_contrato == id_contrato).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    cliente = session.query(Cliente).filter(Cliente.id_cliente == contrato.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    veiculo = session.query(Veiculo).filter(Veiculo.id_veiculo == contrato.id_veiculo).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    financeiro = session.query(Financeiro).filter(Financeiro.id_contrato == contrato.id_contrato).first()
    if not financeiro:
        raise HTTPException(status_code=404, detail="Dados financeiros não encontrados")
    
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
    
    return SolicitacaoDetalheSchema(
        id_contrato=contrato.id_contrato,
        numero_contrato=contrato.num_contrato,
        id_cliente=contrato.id_cliente,
        nome_cliente=cliente.nome,
        cpf_cliente=cliente.cpf,
        email_cliente=cliente.email,
        telefone_cliente=cliente.telefone,
        data_emissao=contrato.data_emissao,
        status=contrato.status,
        veiculo=veiculo_schema,
        financeiro=financeiro_schema
    )


@admin_router.put("/solicitacao/{id_contrato}/aprovar")
async def aprovar_solicitacao(
    id_contrato: int,
    dados: Optional[AprovarRejeitarSchema] = Body(None),
    session: Session = Depends(pegar_sessao)
):
    """
    Aprova uma solicitação, alterando o status do contrato para 'ativo'
    """
    contrato = session.query(Contrato).filter(Contrato.id_contrato == id_contrato).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    if contrato.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Solicitação já foi processada. Status atual: {contrato.status}")
    
    try:
        contrato.status = "ativo"
        session.commit()
        
        return {
            "success": True,
            "message": "Solicitação aprovada com sucesso",
            "id_contrato": contrato.id_contrato,
            "status": contrato.status
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao aprovar solicitação: {str(e)}")


@admin_router.put("/solicitacao/{id_contrato}/rejeitar")
async def rejeitar_solicitacao(
    id_contrato: int,
    dados: Optional[AprovarRejeitarSchema] = Body(None),
    session: Session = Depends(pegar_sessao)
):
    """
    Rejeita uma solicitação, alterando o status do contrato para 'rejeitado'
    """
    contrato = session.query(Contrato).filter(Contrato.id_contrato == id_contrato).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    if contrato.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Solicitação já foi processada. Status atual: {contrato.status}")
    
    try:
        contrato.status = "rejeitado"
        session.commit()
        
        return {
            "success": True,
            "message": "Solicitação rejeitada com sucesso",
            "id_contrato": contrato.id_contrato,
            "status": contrato.status,
            "motivo": dados.motivo if dados else None
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao rejeitar solicitação: {str(e)}")


@admin_router.get("/contratos", response_model=ContratosVigentesResponseSchema)
async def listar_contratos_vigentes(session: Session = Depends(pegar_sessao)):
    """
    Lista todos os contratos vigentes (status 'ativo')
    Retorna informações resumidas para o painel admin
    """
    contratos_ativos = session.query(Contrato).filter(Contrato.status == "ativo").all()
    
    contratos = []
    for contrato in contratos_ativos:
        cliente = session.query(Cliente).filter(Cliente.id_cliente == contrato.id_cliente).first()
        if not cliente:
            continue
        
        veiculo = session.query(Veiculo).filter(Veiculo.id_veiculo == contrato.id_veiculo).first()
        if not veiculo:
            continue
        
        financeiro = session.query(Financeiro).filter(Financeiro.id_contrato == contrato.id_contrato).first()
        if not financeiro:
            continue
        
        contrato_item = ContratoListaSchema(
            id_contrato=contrato.id_contrato,
            numero_contrato=contrato.num_contrato,
            id_cliente=contrato.id_cliente,
            nome_cliente=cliente.nome,
            marca_veiculo=veiculo.marca,
            modelo_veiculo=veiculo.modelo,
            valor_total=float(financeiro.valor_total),
            status=contrato.status,
            data_emissao=contrato.data_emissao
        )
        contratos.append(contrato_item)
    
    return ContratosVigentesResponseSchema(
        contratos=contratos,
        total=len(contratos)
    )


@admin_router.get("/contrato/{id_contrato}", response_model=ContratoCompletoSchema)
async def detalhes_contrato_admin(id_contrato: int, session: Session = Depends(pegar_sessao)):
    """
    Retorna detalhes completos de um contrato específico
    Inclui dados do veículo, financeiro e todas as parcelas
    """
    contrato = session.query(Contrato).filter(Contrato.id_contrato == id_contrato).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    cliente = session.query(Cliente).filter(Cliente.id_cliente == contrato.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    veiculo = session.query(Veiculo).filter(Veiculo.id_veiculo == contrato.id_veiculo).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    financeiro = session.query(Financeiro).filter(Financeiro.id_contrato == contrato.id_contrato).first()
    if not financeiro:
        raise HTTPException(status_code=404, detail="Dados financeiros não encontrados")
    
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
    
    cliente_schema = ClienteInfoSchema(
        id_cliente=cliente.id_cliente,
        nome=cliente.nome,
        cpf=cliente.cpf,
        email=cliente.email,
        telefone=cliente.telefone,
        renda=float(cliente.renda) if cliente.renda else None
    )
    
    return ContratoCompletoSchema(
        id_contrato=contrato.id_contrato,
        numero_contrato=contrato.num_contrato,
        status=contrato.status,
        id_cliente=contrato.id_cliente,
        data_emissao=contrato.data_emissao,
        vigencia_fim=contrato.vigencia_fim,
        veiculo=veiculo_schema,
        financeiro=financeiro_schema,
        cliente=cliente_schema
    )