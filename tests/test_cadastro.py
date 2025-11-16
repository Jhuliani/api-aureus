import pytest
from fastapi.testclient import TestClient
from models import Cliente, Usuario, Endereco


def test_cadastro_valido(client, db_session):
    """
    Testa cadastro completo de cliente.
    Usa try/finally para limpar os dados criados (Cliente → Endereco → Usuario).
    """
    id_cliente = None
    id_usuario = None
    id_endereco = None
    
    try:
        dados_cadastro = {
            "nome": "Novo Cliente",
            "cpf": "98765432100",
            "email": "novo@cliente.com",
            "telefone": "11988888888",
            "renda": 6000.0,
            "logradouro": "Rua Nova",
            "numero": "456",
            "bairro": "Vila Nova",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "cep": "20000000",
            "login": "novo_cliente",
            "senha": "senha123"
        }
        
        response = client.post("/cliente/cadastro-completo", json=dados_cadastro)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id_cliente" in data
        assert "id_usuario" in data
        
        id_cliente = data["id_cliente"]
        id_usuario = data["id_usuario"]
        id_endereco = data["id_endereco"]
        
    finally:
        if id_cliente:
            cliente = db_session.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
            if cliente:
                db_session.delete(cliente)
        
        if id_endereco:
            endereco = db_session.query(Endereco).filter(Endereco.id_endereco == id_endereco).first()
            if endereco:
                db_session.delete(endereco)
        
        if id_usuario:
            usuario = db_session.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
            if usuario:
                db_session.delete(usuario)
        
        db_session.commit()


def test_cadastro_cpf_duplicado(client, usuario_cliente):
    dados_cadastro = {
        "nome": "Outro Cliente",
        "cpf": "12345678901",
        "email": "outro@cliente.com",
        "telefone": "11977777777",
        "renda": 4000.0,
        "logradouro": "Rua Outra",
        "numero": "789",
        "bairro": "Bairro Outro",
        "cidade": "Belo Horizonte",
        "estado": "MG",
        "cep": "30000000",
        "login": "outro_cliente",
        "senha": "senha123"
    }
    
    response = client.post("/cliente/cadastro-completo", json=dados_cadastro)
    assert response.status_code == 400
    assert "CPF já cadastrado" in response.json()["detail"]


