import pytest
from fastapi.testclient import TestClient
from models import Cliente, Veiculo, Contrato, Financeiro, Parcela


def test_criar_solicitacao_valida(client, token_cliente, usuario_cliente, db_session):
    """
    Testa criação de solicitação de financiamento.
    Usa try/finally para limpar os dados criados (Parcela → Financeiro → Contrato → Veiculo).
    """
    id_contrato = None
    id_veiculo = None
    id_financeiro = None
    
    try:
        cliente = db_session.query(Cliente).filter(Cliente.id_usuario == usuario_cliente.id_usuario).first()
        
        dados_solicitacao = {
            "id_cliente": cliente.id_cliente,
            "tipoVeiculo": "carros",
            "marcaSelecionada": "1",
            "marcaNome": "Fiat",
            "modeloSelecionado": "1",
            "modeloNome": "Uno",
            "anoSelecionado": "2024-1",
            "veiculo": {
                "placa": "ABC1234",
                "numChassi": "9BW12345678901234",
                "numRenavam": "12345678901",
                "cor": "Branco"
            },
            "financeiro": {
                "valorVeiculo": 50000.0,
                "valorEntrada": 10000.0,
                "parcelasSelecionadas": 36,
                "taxaJuros": 1.5,
                "rendaMensal": 5000.0,
                "valorFinanciado": 40000.0,
                "valorParcela": 1500.0,
                "totalPagar": 54000.0,
                "totalJuros": 14000.0
            }
        }
        
        response = client.post(
            "/cliente/solicitacao",
            json=dados_solicitacao,
            headers={"Authorization": f"Bearer {token_cliente}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id_contrato" in data
        assert "numero_contrato" in data
        
        id_contrato = data["id_contrato"]
        id_veiculo = data["id_veiculo"]
        id_financeiro = data["id_financeiro"]
        
    finally:
        if id_financeiro:
            db_session.query(Parcela).filter(Parcela.id_financeiro == id_financeiro).delete()
            financeiro = db_session.query(Financeiro).filter(Financeiro.id_financeiro == id_financeiro).first()
            if financeiro:
                db_session.delete(financeiro)
        
        if id_contrato:
            contrato = db_session.query(Contrato).filter(Contrato.id_contrato == id_contrato).first()
            if contrato:
                db_session.delete(contrato)
        
        if id_veiculo:
            veiculo = db_session.query(Veiculo).filter(Veiculo.id_veiculo == id_veiculo).first()
            if veiculo:
                db_session.delete(veiculo)
        
        db_session.commit()

