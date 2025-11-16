import pytest
from fastapi.testclient import TestClient


def test_login_valido(client, usuario_cliente):
    response = client.post(
        "/auth/login",
        json={"login": "cliente_teste", "senha": "senha123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "id_cliente" in data
    assert data["id_cliente"] is not None


def test_login_invalido(client):
    response = client.post(
        "/auth/login",
        json={"login": "usuario_inexistente", "senha": "senha_errada"}
    )
    assert response.status_code == 400
    assert "Usuário não encontrado" in response.json()["detail"] or "credenciais inválidas" in response.json()["detail"]


