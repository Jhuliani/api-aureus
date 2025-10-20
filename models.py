from sqlalchemy import create_engine, Column, String, Integer, Date, Numeric, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils.types import ChoiceType

#cria a conexão
db = create_engine("url")

#cria a base do banco de dados
Base = declarative_base()

class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column("id_ciente", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    cpf = Column("cpf", String, nullable=False)
    telefone = Column("telefone", String)
    estado = Column("estado", String)
    bairro = Column("bairro", String)
    rua = Column("rua", String)
    numero = Column("numero", String)
    cep = Column("cep", String)
    renda = Column("renda", String)
    nome_pai = Column("nome_pai", String)
    nome_mae = Column("nome_mae", String)

    def __init__(self, nome, cpf, telefone, estado, bairro, rua,numero, cep, renda, nome_pai, nome_mae):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.estado = estado
        self.bairro = bairro
        self.rua = rua
        self.numero = numero
        self.cep = cep
        self.renda = renda
        self.nome_mae = nome_mae
        self.nome_pai =  nome_pai

class Contrato(Base):
    __tablename__ = "contrato"

    id_contrato = Column("id_contrato", Integer, primary_key=True, autoincrement=True)
    num_contrato = Column("num_contrato", String)
    data_emissao = Column("data_emissao", Date)
    vigencia_ctt = Column("vigencia_ctt", String)
    status = Column("status", String)
    data = Column("data", Date)
    id_cliente = Column("id_cliente", Integer)
    id_veiculo = Column("id_veiculo", Integer)
    id_financiamento = Column("id_financiamento", Integer)

    def __init__(self, id_contrato, num_contrato, data_emissao, vigencia_ctt, status, data,id_cliente, id_veiculo, id_financiamento):
        self.id_contrato = id_contrato
        self.num_contrato = num_contrato
        self.data_emissao = data_emissao
        self.vigencia_ctt = vigencia_ctt
        self.status = status
        self.data = data
        self.id_cliente = id_cliente
        self.id_veiculo = id_veiculo
        self.id_financiamento = id_financiamento

class Financeiro(Base):
    __tablename__ = "financeiro"

    id_financeiro = Column("id_financeiro", Integer, primary_key=True, autoincrement=True)
    qtde_parcelas = Column("qtde_parcelas", Integer)
    prazo = Column("prazo", Integer)
    status_parcelas = Column("status_parcelas", String)
    valor_entrada = Column("valor_entrada", Numeric)
    valor_parcelas = Column("valor_parcelas", Numeric)
    valor_financiar = Column("valor_financiar", Numeric)

    def __init__(self, id_financeiro, qtde_parcelas, prazo, status_parcelas, valor_entrada, valor_parcelas,valor_financiar):
        self.id_financeiro = id_financeiro
        self.qtde_parcelas = qtde_parcelas
        self.prazo = prazo
        self.status_parcelas = status_parcelas
        self.valor_entrada = valor_entrada
        self.valor_parcelas = valor_parcelas
        self.valor_financiar = valor_financiar

class Perfil(Base):
    __tablename__ = "perfil"

    id_perfil = Column("id_perfil", Integer, primary_key=True, autoincrement=True)
    nome_perfil = Column("nome_perfil", String)
    nivel_acesso = Column("nivel_acesso", Date)

    def __init__(self, nome_perfil, nivel_acesso):
        self.nome_perfil = nome_perfil
        self.nivel_acesso = nivel_acesso

class Usuario(Base):
    __tablename__ = "usuario"

    id_user = Column("id_user", Integer, primary_key=True, autoincrement=True)
    login = Column("login", String)
    senha = Column("senha", String)
    id_perfil = Column("id_perfil", Integer)

    def __init__(self, login, senha,id_perfil):
        self.login = login
        self.senha = senha
        self.id_perfil = id_perfil


class Veiculo(Base):
    __tablename__ = "veiculo"

    id_veiculo = Column("id_veiculo", Integer, primary_key=True, autoincrement=True)
    valor = Column("valor", Numeric)
    placa = Column("placa", String)
    ano_modelo = Column("ano_modelo", Integer)
    marca_modelo = Column("marca_modelo", String)
    cor_predominante = Column("cor_predominante", String)
    num_chassi = Column("num_chassi", String)
    num_renavam = Column("num_renavam", String)

    def __init__(self, id_veiculo, valor, placa, ano_modelo, marca_modelo, cor_predominante,num_chassi,num_renavam):
        self.id_veiculo = id_veiculo
        self.valor = valor
        self.placa = placa
        self.ano_modelo = ano_modelo
        self.marca_modelo = marca_modelo
        self.cor_predominante = cor_predominante
        self.num_chassi = num_chassi
        self.num_renavam = num_renavam