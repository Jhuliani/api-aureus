import pytest
from fastapi.testclient import TestClient


def test_listar_contratos_cliente(client, token_cliente, cliente_id):
    response = client.get(
        f"/cliente/contratos/{cliente_id}",
        headers={"Authorization": f"Bearer {token_cliente}"}
    )
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "contratos" in data
        assert "total" in data

