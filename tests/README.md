# Testes da API

## Executar Testes

Para executar todos os testes:

```bash
pytest
```

Para executar com mais detalhes:

```bash
pytest -v
```

Para executar um arquivo específico:

```bash
pytest tests/test_auth.py
```

## Estrutura dos Testes

- `conftest.py` - Fixtures compartilhadas (client, usuários, tokens)
- `test_auth.py` - Testes de autenticação
- `test_cadastro.py` - Testes de cadastro
- `test_solicitacao.py` - Testes de solicitação
- `test_contratos.py` - Testes de contratos
  