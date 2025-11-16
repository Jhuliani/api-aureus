import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from models import Base, Usuario, Cliente, Endereco
from main import app, limiter
from dependencies import pegar_sessao
import bcrypt
from datetime import date
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#troca o banco oficial pelo de teste
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

#quando alguem pedir  pegar_sessao vai usar o override em vez do original
app.dependency_overrides[pegar_sessao] = override_get_db

#substitui a função que identifica ip, o rate limiter pode nao funcionar nos testes
def get_remote_address_override():
    return "127.0.0.1"

limiter.key_func = get_remote_address_override


@pytest.fixture(scope="function")
def client():
    """
    Cria as tabelas uma vez no início dos testes.
    A limpeza é feita manualmente nas fixtures que criam dados.
    """
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def usuario_cliente(db_session):
    """
    Cria usuário, endereço e cliente para testes.
    Usa try/finally para garantir limpeza mesmo se der erro.
    """
    usuario = None
    endereco = None
    cliente = None
    
    try:
        senha_hash = bcrypt.hashpw("senha123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        usuario = Usuario(
            id_perfil=1,
            login="cliente_teste",
            senha_hash=senha_hash,
            data_criacao=date.today()
        )
        db_session.add(usuario)
        db_session.flush()
        
        endereco = Endereco(
            logradouro="Rua Teste",
            numero="123",
            bairro="Centro",
            cidade="São Paulo",
            estado="SP",
            cep="01234567"
        )
        db_session.add(endereco)
        db_session.flush()
        
        cliente = Cliente(
            id_usuario=usuario.id_usuario,
            id_endereco=endereco.id_endereco,
            nome="Cliente Teste",
            cpf="12345678901",
            email="cliente@teste.com",
            telefone="11999999999",
            renda=5000.0,
            data_cadastro=date.today()
        )
        db_session.add(cliente)
        db_session.commit()
        
        yield usuario  
        
    finally:
        if cliente:
            db_session.delete(cliente)
        if endereco:
            db_session.delete(endereco)
        if usuario:
            db_session.delete(usuario)
        db_session.commit()


@pytest.fixture
def token_cliente(client, usuario_cliente):
    response = client.post(
        "/auth/login",
        json={"login": "cliente_teste", "senha": "senha123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def cliente_id(db_session, usuario_cliente):
    from models import Cliente
    cliente = db_session.query(Cliente).filter(Cliente.id_usuario == usuario_cliente.id_usuario).first()
    return cliente.id_cliente

