# 📋 Estrutura do Backend - Aureus-Bank WS

## 🎯 Visão Geral

O **aureus-bank-ws** é uma API REST desenvolvida com **FastAPI** que gerencia o sistema de financiamento veicular. A aplicação utiliza **SQLAlchemy** para ORM, **Alembic** para migrações de banco de dados e **JWT** para autenticação.

---

## 📁 Arquitetura de Pastas

```
aureus-bank-ws/
├── alembic/              # Migrações de banco de dados
│   ├── versions/         # Histórico de migrações
│   └── env.py           # Configuração do Alembic
├── routes/               # Rotas da API (endpoints)
│   ├── auth_routes.py   # Rotas de autenticação
│   ├── cliente_routes.py # Rotas do cliente
│   └── admin_routes.py  # Rotas do administrador
├── models.py             # Modelos SQLAlchemy (entidades do banco)
├── schemas.py            # Schemas Pydantic (validação de dados)
├── dependencies.py      # Dependências compartilhadas (sessão DB, auth)
├── main.py              # Aplicação FastAPI principal
├── alembic.ini          # Configuração do Alembic
└── requirements.txt     # Dependências Python
```

---

## 🗄️ Modelos de Dados (`models.py`)

### Estrutura do Banco de Dados

O sistema utiliza as seguintes entidades principais:

#### **Perfil**
- `id_perfil` (PK)
- `nome` - Nome do perfil (ex: "admin", "cliente")
- Relacionamento: 1:N com `Usuario`

#### **Usuario**
- `id_usuario` (PK)
- `id_perfil` (FK → Perfil)
- `login` - Login único
- `senha_hash` - Senha criptografada (bcrypt)
- `data_criacao` - Data de criação
- Relacionamentos:
  - 1:1 com `Cliente`
  - N:1 com `Perfil`

#### **Endereco**
- `id_endereco` (PK)
- `logradouro`, `numero`, `bairro`, `cidade`, `estado`, `cep`
- Relacionamento: 1:N com `Cliente`

#### **Cliente**
- `id_cliente` (PK)
- `id_usuario` (FK → Usuario, único)
- `id_endereco` (FK → Endereco)
- `nome`, `cpf` (único), `email` (único), `telefone`, `renda`
- `data_cadastro` - Data de cadastro
- Relacionamentos:
  - 1:1 com `Usuario`
  - N:1 com `Endereco`
  - 1:N com `Contrato`

#### **Veiculo**
- `id_veiculo` (PK)
- `marca`, `modelo`, `ano_fabricacao`, `ano_modelo`
- `cor`, `placa` (único), `num_chassi` (único), `num_renavam` (único)
- `valor` - Valor do veículo
- Relacionamento: 1:1 com `Contrato`

#### **Contrato**
- `id_contrato` (PK)
- `id_cliente` (FK → Cliente)
- `id_veiculo` (FK → Veiculo, único)
- `num_contrato` - Número único do contrato
- `data_emissao`, `vigencia_fim`
- `status` - Status do contrato (ex: "ativo", "cancelado")
- Relacionamentos:
  - N:1 com `Cliente`
  - 1:1 com `Veiculo`
  - 1:1 com `Financeiro`

#### **Financeiro**
- `id_financeiro` (PK)
- `id_contrato` (FK → Contrato, único)
- `valor_total`, `valor_entrada`, `taxa_juros`
- `qtde_parcelas` - Quantidade de parcelas
- `data_primeiro_vencimento`
- `status_pagamento` - Status (ex: "em_dia", "atrasado")
- `data_criacao`
- Relacionamentos:
  - 1:1 com `Contrato`
  - 1:N com `Parcela`

#### **Parcela**
- `id_parcela` (PK)
- `id_financeiro` (FK → Financeiro)
- `numero_parcela` - Número da parcela
- `valor_parcela`, `data_vencimento`
- `data_pagamento`, `valor_pago`
- `status` - Status (ex: "pendente", "paga", "atrasada")
- Constraint: `(id_financeiro, numero_parcela)` único

---

## 📝 Schemas Pydantic (`schemas.py`)

Schemas utilizados para validação de entrada e saída da API:

### Autenticação
- **`LoginSchema`** - Dados de login (login, senha)
- **`UsuarioSchema`** - Dados de usuário (login, senha, id_perfil)

### Cliente
- **`ClienteCompletoSchema`** - Cadastro completo (dados pessoais + endereço + usuário)

### Contratos
- **`ContratoDetalhadoSchema`** - Informações básicas do contrato
- **`ContratoCompletoSchema`** - Contrato completo (com veículo e financeiro)
- **`ContratosResponseSchema`** - Resposta com lista de contratos e total

### Financeiro
- **`FinanceiroSchema`** - Dados de financiamento (simulação)
- **`FinanceiroCompletoSchema`** - Financeiro completo (com parcelas)
- **`ParcelaSchema`** - Dados de uma parcela

### Veículos
- **`VeiculoSchema`** - Dados básicos do veículo
- **`VeiculoCompletoSchema`** - Veículo completo
- **`InformacoesFipeSchema`** - Dados da API FIPE

### Solicitações
- **`SimulacaoSchema`** - Dados de simulação
- **`SolicitacaoSchema`** - Dados de solicitação
- **`SolicitacaoCompletaSchema`** - Solicitação completa (com veículo e financeiro)

---

## 🛣️ Rotas da API (`routes/`)

### Autenticação (`auth_routes.py`)

**Prefixo:** `/auth`

| Método | Endpoint | Descrição | Rate Limit |
|--------|----------|-----------|------------|
| `GET` | `/` | Rota padrão de autenticação | - |
| `POST` | `/login` | Login de usuário | - |
| `POST` | `/login-form` | Login via formulário OAuth2 | 5/min |
| `GET` | `/refresh` | Renovar access token | 10/min |

**Resposta do Login:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "Bearer",
  "id_cliente": 1,
  "nome_cliente": "string",
  "id_perfil": 2,
  "id_usuario": 1
}
```

### Cliente (`cliente_routes.py`)

**Prefixo:** `/cliente`

| Método | Endpoint | Descrição | Auth | Rate Limit |
|--------|----------|-----------|------|------------|
| `POST` | `/cadastro-completo` | Cadastro completo do cliente | ❌ | 3/min |
| `GET` | `/contratos/{id_cliente}` | Lista contratos do cliente | ✅ | - |
| `GET` | `/contrato/{id_contrato}` | Detalhes de um contrato | ✅ | - |
| `POST` | `/solicitacao` | Criar solicitação de financiamento | ✅ | - |

**Nota:** Rotas marcadas com ✅ requerem token JWT válido.

### Administrador (`admin_routes.py`)

**Prefixo:** `/admin`

**Status:** Em desenvolvimento (estrutura criada, rotas a implementar)

Todas as rotas do admin requerem:
- Token JWT válido
- Perfil de administrador

---

## 🔐 Sistema de Autenticação

### JWT (JSON Web Tokens)

- **Biblioteca:** `python-jose`
- **Algoritmo:** Configurável via `.env` (padrão: HS256)
- **Secret Key:** Configurável via `.env`
- **Expiração:** Configurável via `.env` (padrão: minutos)

### Criptografia de Senhas

- **Biblioteca:** `bcrypt` (via `passlib`)
- **Contexto:** `CryptContext` com scheme "bcrypt"
- Senhas são hasheadas antes de serem armazenadas

### Dependências de Autenticação (`dependencies.py`)

#### `verificar_token`
- Valida o token JWT
- Extrai informações do usuário
- Verifica se o usuário existe no banco
- Retorna objeto `Usuario` ou levanta `HTTPException(401)`

#### `pegar_sessao`
- Gerencia sessões do SQLAlchemy
- Cria e fecha sessões automaticamente
- Utiliza `sessionmaker` com o engine do banco

---

## 🗄️ Gerenciamento de Banco de Dados

### SQLAlchemy ORM

- **Engine:** Criado a partir de `DATABASE_URL` (variável de ambiente)
- **Base:** `declarative_base()` para modelos
- **Sessões:** Gerenciadas via `sessionmaker` em `dependencies.py`

### Migrações (Alembic)

- **Configuração:** `alembic.ini` e `alembic/env.py`
- **Versões:** Armazenadas em `alembic/versions/`
- **Base de Metadados:** Importada de `models.Base`

**Comandos úteis:**
```bash
# Criar nova migração
alembic revision --autogenerate -m "descrição"

# Aplicar migrações
alembic upgrade head

# Reverter migração
alembic downgrade -1
```

---

## ⚙️ Configuração (`main.py`)

### FastAPI App

- **CORS:** Habilitado para todas as origens (`allow_origins=["*"]`)
- **Rate Limiting:** Utiliza `slowapi` com `Limiter`
- **Middleware:** CORSMiddleware configurado

### Variáveis de Ambiente

O projeto utiliza `.env` para configurações sensíveis:

```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=sua-chave-secreta-jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Dependências Globais

- **`bcrypt_context`** - Contexto de criptografia de senhas
- **`oauth2_schema`** - Schema OAuth2 para autenticação
- **`limiter`** - Rate limiter global

---

## 🚦 Rate Limiting

O sistema utiliza **slowapi** para limitar requisições:

- **`/auth/login-form`**: 5 requisições/minuto
- **`/auth/refresh`**: 10 requisições/minuto
- **`/cliente/cadastro-completo`**: 3 requisições/minuto

**Chave de identificação:** Endereço IP do cliente (`get_remote_address`)

---

## 🔄 Fluxo de Requisições

```
Cliente → FastAPI → Dependencies (Auth/Session) → Routes → Services → Database
                ↓
         Rate Limiting
                ↓
         CORS Middleware
                ↓
         Response (JSON)
```

---

## 📦 Dependências Principais

### Core
- **FastAPI 0.119.0** - Framework web
- **SQLAlchemy 2.0.44** - ORM
- **Pydantic 2.12.3** - Validação de dados
- **Uvicorn 0.38.0** - Servidor ASGI

### Autenticação
- **python-jose 3.5.0** - JWT
- **passlib 1.7.4** - Criptografia de senhas
- **bcrypt 5.0.0** - Hashing de senhas

### Banco de Dados
- **psycopg2 2.9.11** - Driver PostgreSQL
- **Alembic 1.17.0** - Migrações

### Segurança
- **slowapi 0.1.9** - Rate limiting
- **python-dotenv 1.1.1** - Variáveis de ambiente

---

## 🏗️ Padrões Arquiteturais

### 1. Separação de Responsabilidades
- **Models:** Definição de entidades (SQLAlchemy)
- **Schemas:** Validação e serialização (Pydantic)
- **Routes:** Endpoints da API
- **Dependencies:** Lógica compartilhada (auth, sessão)

### 2. Dependency Injection
- FastAPI utiliza injeção de dependências nativa
- `Depends()` para injetar dependências
- Reutilização de lógica (sessão DB, autenticação)

### 3. Transações de Banco
- Sessões gerenciadas via context managers
- `session.commit()` para confirmar transações
- `session.rollback()` em caso de erro

### 4. Tratamento de Erros
- `HTTPException` para erros HTTP padronizados
- Validação automática via Pydantic
- Mensagens de erro descritivas

---

## 🔒 Segurança

### Implementado
- ✅ Autenticação JWT
- ✅ Criptografia de senhas (bcrypt)
- ✅ Rate limiting
- ✅ Validação de dados (Pydantic)
- ✅ CORS configurado

### Recomendações
- ⚠️ Restringir CORS em produção (não usar `["*"]`)
- ⚠️ Implementar HTTPS
- ⚠️ Adicionar logging de segurança
- ⚠️ Implementar refresh token rotation
- ⚠️ Adicionar validação de perfil nas rotas admin

---

## 📝 Convenções de Código

### Nomenclatura
- **Rotas:** snake_case (ex: `cadastrar_cliente_completo`)
- **Modelos:** PascalCase (ex: `Cliente`, `Contrato`)
- **Schemas:** PascalCase + "Schema" (ex: `ClienteCompletoSchema`)
- **Variáveis:** snake_case

### Estrutura de Rotas
```python
@router.method("/endpoint")
@limiter.limit("X/minute")  # Opcional
async def nome_funcao(
    request: Request,  # Se usar rate limiting
    dados: Schema,     # Schema Pydantic
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)  # Se requer auth
):
    # Lógica da rota
```

---

## 🚀 Executando o Projeto

### Desenvolvimento
```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (.env)
# Executar migrações
alembic upgrade head

# Iniciar servidor
uvicorn main:app --reload
```

### Produção
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Estrutura de Respostas

### Sucesso
```json
{
  "success": true,
  "data": {...},
  "message": "Operação realizada com sucesso"
}
```

### Erro
```json
{
  "detail": "Mensagem de erro descritiva"
}
```

---

## 🎯 Próximos Passos Sugeridos

1. Implementar rotas do admin
2. Adicionar testes unitários e de integração
3. Implementar logging estruturado
4. Adicionar documentação Swagger customizada
5. Implementar cache (Redis)
6. Adicionar monitoramento e métricas
7. Implementar validação de perfil nas rotas
8. Adicionar documentação de API (OpenAPI)

