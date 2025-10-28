from sqlalchemy import create_engine, Column, String, Integer, Date, Numeric, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv
import os

load_dotenv()

#cria a conexão
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
db = create_engine(DATABASE_URL)

#cria a base do banco de dados
Base = declarative_base()

# =======================
# TABELA PERFIL
# =======================
class Perfil(Base):
    __tablename__ = "perfil"

    id_perfil = Column("id_perfil", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(100), nullable=False)

    # Relacionamentos
    usuarios = relationship("Usuario", back_populates="perfil")

    def __init__(self, nome):
        self.nome = nome


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column("id_usuario", Integer, primary_key=True, autoincrement=True)
    id_perfil = Column("id_perfil", Integer, ForeignKey("perfil.id_perfil"), nullable=False)
    login = Column("login", String(100), unique=True, nullable=False)
    senha_hash = Column("senha_hash", String(255), nullable=False)
    data_criacao = Column("data_criacao", Date, default=Date)

    # Relacionamentos
    perfil = relationship("Perfil", back_populates="usuarios")
    cliente = relationship("Cliente", back_populates="usuario", uselist=False)

    def __init__(self, id_perfil, login, senha_hash, data_criacao=None):
        self.id_perfil = id_perfil
        self.login = login
        self.senha_hash = senha_hash
        self.data_criacao = data_criacao

# =======================
# TABELA ENDERECO
# =======================
class Endereco(Base):
    __tablename__ = "endereco"

    id_endereco = Column("id_endereco", Integer, primary_key=True, autoincrement=True)
    logradouro = Column("logradouro", String(150), nullable=False)
    numero = Column("numero", String(10))
    bairro = Column("bairro", String(80), nullable=False)
    cidade = Column("cidade", String(80), nullable=False)
    estado = Column("estado", String(2), nullable=False)
    cep = Column("cep", String(9), nullable=False)

    # Relacionamentos
    clientes = relationship("Cliente", back_populates="endereco")

    def __init__(self, logradouro, numero, bairro, cidade, estado, cep):
        self.logradouro = logradouro
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column("id_cliente", Integer, primary_key=True, autoincrement=True)
    id_usuario = Column("id_usuario", Integer, ForeignKey("usuario.id_usuario"), unique=True, nullable=False)
    id_endereco = Column("id_endereco", Integer, ForeignKey("endereco.id_endereco"), nullable=False)
    nome = Column("nome", String(120), nullable=False)
    cpf = Column("cpf", String(11), unique=True, nullable=False)
    email = Column("email", String(150), unique=True, nullable=False)
    telefone = Column("telefone", String(20))
    renda = Column("renda", Numeric(10, 2))
    data_cadastro = Column("data_cadastro", Date, default=Date)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="cliente")
    endereco = relationship("Endereco", back_populates="clientes")
    contratos = relationship("Contrato", back_populates="cliente")

    def __init__(self, id_usuario, id_endereco, nome, cpf, email, telefone=None, renda=None, data_cadastro=None):
        self.id_usuario = id_usuario
        self.id_endereco = id_endereco
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.telefone = telefone
        self.renda = renda
        self.data_cadastro = data_cadastro


class Veiculo(Base):
    __tablename__ = "veiculo"

    id_veiculo = Column("id_veiculo", Integer, primary_key=True, autoincrement=True)
    marca = Column("marca", String(80), nullable=False)
    modelo = Column("modelo", String(80), nullable=False)
    ano_fabricacao = Column("ano_fabricacao", Integer, nullable=False)
    ano_modelo = Column("ano_modelo", Integer, nullable=False)
    cor = Column("cor", String(40))
    placa = Column("placa", String(10), unique=True)
    num_chassi = Column("num_chassi", String(20), unique=True, nullable=False)
    num_renavam = Column("num_renavam", String(20), unique=True, nullable=False)
    valor = Column("valor", Numeric(12, 2), nullable=False)

    # Relacionamentos
    contrato = relationship("Contrato", back_populates="veiculo", uselist=False)

    def __init__(self, marca, modelo, ano_fabricacao, ano_modelo, cor, placa, num_chassi, num_renavam, valor):
        self.marca = marca
        self.modelo = modelo
        self.ano_fabricacao = ano_fabricacao
        self.ano_modelo = ano_modelo
        self.cor = cor
        self.placa = placa
        self.num_chassi = num_chassi
        self.num_renavam = num_renavam
        self.valor = valor


class Contrato(Base):
    __tablename__ = "contrato"

    id_contrato = Column("id_contrato", Integer, primary_key=True, autoincrement=True)
    id_cliente = Column("id_cliente", Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    id_veiculo = Column("id_veiculo", Integer, ForeignKey("veiculo.id_veiculo"), unique=True, nullable=False)
    num_contrato = Column("num_contrato", String(50), unique=True, nullable=False)
    data_emissao = Column("data_emissao", Date, nullable=False)
    vigencia_fim = Column("vigencia_fim", Date)
    status = Column("status", String(30), default="ativo")

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="contratos")
    veiculo = relationship("Veiculo", back_populates="contrato")
    financeiro = relationship("Financeiro", back_populates="contrato", uselist=False)

    def __init__(self, id_cliente, id_veiculo, num_contrato, data_emissao, vigencia_fim=None, status="ativo"):
        self.id_cliente = id_cliente
        self.id_veiculo = id_veiculo
        self.num_contrato = num_contrato
        self.data_emissao = data_emissao
        self.vigencia_fim = vigencia_fim
        self.status = status

class Financeiro(Base):
    __tablename__ = "financeiro"

    id_financeiro = Column("id_financeiro", Integer, primary_key=True, autoincrement=True)
    id_contrato = Column("id_contrato", Integer, ForeignKey("contrato.id_contrato"), unique=True, nullable=False)
    valor_total = Column("valor_total", Numeric(12, 2), nullable=False)
    valor_entrada = Column("valor_entrada", Numeric(12, 2), default=0)
    taxa_juros = Column("taxa_juros", Numeric(5, 2))
    qtde_parcelas = Column("qtde_parcelas", Integer, nullable=False)
    data_primeiro_vencimento = Column("data_primeiro_vencimento", Date, nullable=False)
    status_pagamento = Column("status_pagamento", String(30), default="em_dia")
    data_criacao = Column("data_criacao", Date, default=Date)

    # Relacionamentos
    contrato = relationship("Contrato", back_populates="financeiro")
    parcelas = relationship("Parcela", back_populates="financeiro")

    def __init__(self, id_contrato, valor_total, valor_entrada=0, taxa_juros=None, qtde_parcelas=None, 
                 data_primeiro_vencimento=None, status_pagamento="em_dia", data_criacao=None):
        self.id_contrato = id_contrato
        self.valor_total = valor_total
        self.valor_entrada = valor_entrada
        self.taxa_juros = taxa_juros
        self.qtde_parcelas = qtde_parcelas
        self.data_primeiro_vencimento = data_primeiro_vencimento
        self.status_pagamento = status_pagamento
        self.data_criacao = data_criacao

class Parcela(Base):
    __tablename__ = "parcela"

    id_parcela = Column("id_parcela", Integer, primary_key=True, autoincrement=True)
    id_financeiro = Column("id_financeiro", Integer, ForeignKey("financeiro.id_financeiro"), nullable=False)
    numero_parcela = Column("numero_parcela", Integer, nullable=False)
    valor_parcela = Column("valor_parcela", Numeric(12, 2), nullable=False)
    data_vencimento = Column("data_vencimento", Date, nullable=False)
    data_pagamento = Column("data_pagamento", Date)
    valor_pago = Column("valor_pago", Numeric(12, 2))
    status = Column("status", String(30), default="pendente")

    # Relacionamentos
    financeiro = relationship("Financeiro", back_populates="parcelas")

    # Constraints
    __table_args__ = (
        UniqueConstraint('id_financeiro', 'numero_parcela', name='uq_financeiro_numero_parcela'),
    )

    def __init__(self, id_financeiro, numero_parcela, valor_parcela, data_vencimento, 
                 data_pagamento=None, valor_pago=None, status="pendente"):
        self.id_financeiro = id_financeiro
        self.numero_parcela = numero_parcela
        self.valor_parcela = valor_parcela
        self.data_vencimento = data_vencimento
        self.data_pagamento = data_pagamento
        self.valor_pago = valor_pago
        self.status = status