# Aureus Bank - API Backend

API REST desenvolvida em FastAPI para o sistema de financiamento de veículos Aureus Bank.

## Índice

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Executando a Aplicação](#executando-a-aplicação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Rotas da API](#rotas-da-api)
- [Testes](#testes)
- [Migrações do Banco de Dados](#migrações-do-banco-de-dados)
- [Documentação da API](#documentação-da-api)

## Requisitos

- **Python**: 3.10 ou superior
- **pip**: Gerenciador de pacotes Python
- **PostgreSQL**: Para produção (opcional, SQLite para desenvolvimento)
- **Git**: Para clonar o repositório

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/Jhuliani/api-aureus.git
cd aureus-bank-ws
```

### 2. Crie um ambiente virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## Configuração

### 1. Crie o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Banco de Dados
# Para desenvolvimento (SQLite):
DATABASE_URL=sqlite:///./database.db

# Para produção (PostgreSQL):
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/aureus_db

# JWT - Autenticação
SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Executando a Aplicação

### Modo Desenvolvimento

```bash
uvicorn main:app --reload
```

A API estará disponível em:
- **API**: `http://localhost:8000`
- **Documentação Swagger**: `http://localhost:8000/docs`
- **Documentação ReDoc**: `http://localhost:8000/redoc`


## Estrutura do Projeto

```
aureus-bank-ws/
├── alembic/              # Migrações do banco de dados
│   ├── versions/         # Versões das migrações
│   └── env.py           # Configuração do Alembic
├── routes/               # Rotas da API
│   ├── auth_routes.py   # Rotas de autenticação
│   ├── cliente_routes.py # Rotas do cliente
│   └── admin_routes.py  # Rotas do administrador
├── tests/                # Testes automatizados
│   ├── conftest.py      # Configuração e fixtures
│   ├── test_auth.py     # Testes de autenticação
│   ├── test_cadastro.py # Testes de cadastro
│   ├── test_solicitacao.py # Testes de solicitação
│   └── test_contratos.py # Testes de contratos
├── main.py              # Arquivo principal da aplicação
├── models.py            # Modelos do banco de dados (SQLAlchemy)
├── schemas.py           # Schemas Pydantic para validação
├── dependencies.py      # Dependências (sessão DB, verificação de token)
├── requirements.txt     # Dependências Python
├── alembic.ini          # Configuração do Alembic
├── pytest.ini           # Configuração do Pytest
└── .env                 # Variáveis de ambiente (não versionado)
```

## Rotas da API

### Autenticação (`/auth`)

- `GET /auth/` - Rota padrão
- `POST /auth/login` - Login (retorna access_token e refresh_token)
- `POST /auth/login-form` - Login via formulário OAuth2
- `GET /auth/refresh` - Renovar access_token

### Cliente (`/cliente`)

- `POST /cliente/cadastro-completo` - Cadastro completo de cliente
- `GET /cliente/contratos/{id_cliente}` - Listar contratos do cliente
- `GET /cliente/contrato/{id_contrato}` - Detalhes de um contrato
- `POST /cliente/solicitacao` - Criar solicitação de financiamento

### Admin (`/admin`)

Todas as rotas de admin requerem autenticação e perfil de administrador.

- `GET /admin/dashboard/metrics` - Métricas do dashboard
- `GET /admin/solicitacoes` - Listar solicitações pendentes
- `GET /admin/solicitacao/{id_contrato}` - Detalhes de uma solicitação
- `PUT /admin/solicitacao/{id_contrato}/aprovar` - Aprovar solicitação
- `PUT /admin/solicitacao/{id_contrato}/rejeitar` - Rejeitar solicitação
- `GET /admin/contratos` - Listar todos os contratos
- `GET /admin/contrato/{id_contrato}` - Detalhes de um contrato

**Documentação completa:** Acesse `http://localhost:8000/docs` quando a API estiver rodando.

## Testes

### Executando os Testes

```bash
# Todos os testes
pytest

# Com mais detalhes
pytest -v

# Um arquivo específico
pytest tests/test_auth.py

# Com cobertura (se configurado)
pytest --cov=.
```

### Estrutura de Testes

- **Banco de teste**: SQLite isolado (`test.db`)
- **Fixtures**: Configuradas em `conftest.py`
- **Limpeza**: Automática após cada teste

### Fixtures Disponíveis

- `client` - Cliente HTTP para testes
- `db_session` - Sessão do banco de dados
- `usuario_cliente` - Usuário cliente para testes
- `token_cliente` - Token JWT para testes
- `cliente_id` - ID do cliente de teste

## Migrações do Banco de Dados

O projeto utiliza **Alembic** para controle de versão do banco de dados.

### Criar uma Nova Migração

```bash
alembic revision --autogenerate -m "descrição da migração"
```

### Aplicar Migrações

```bash
# Aplicar todas as migrações pendentes
alembic upgrade head

# Aplicar próxima migração
alembic upgrade +1
```

### Reverter Migrações

```bash
# Reverter última migração
alembic downgrade -1

# Reverter todas
alembic downgrade base
```

### Ver Status das Migrações

```bash
alembic current
alembic history
```
