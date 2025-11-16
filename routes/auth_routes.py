from fastapi import APIRouter, Depends, HTTPException, Request
from models import Usuario, Cliente
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, limiter
from schemas import LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

def autenticar_usuario(login, senha, session):
    import bcrypt
    usuario = session.query(Usuario).filter(Usuario.login==login).first()
    
    if not usuario:
        return False
    
    senha_bytes = senha.encode('utf-8')
    hash_bytes = usuario.senha_hash.encode('utf-8')
    
    senha_ok = bcrypt.checkpw(senha_bytes, hash_bytes)
    
    if not senha_ok:
        return False
    
    return usuario


@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema
    """
    return {"mensagem": "Você acessou a rota padrão de autenticação", "autenticado": False}

@auth_router.post("/login")
@limiter.limit("5/minute")  
async def login(request: Request, login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.login, login_schema.senha, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        cliente = session.query(Cliente).filter(Cliente.id_usuario == usuario.id_usuario).first()
        
        if not cliente:
            raise HTTPException(status_code=400, detail="Cliente não encontrado para este usuário")
        
        access_token = criar_token(usuario.id_usuario)
        refresh_token = criar_token(usuario.id_usuario, duracao_token=timedelta(days=7))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "id_cliente": cliente.id_cliente,
            "nome_cliente": cliente.nome,
            "id_perfil": usuario.id_perfil,
            "id_usuario": usuario.id_usuario
        }
    
@auth_router.post("/login-form")
@limiter.limit("5/minute")  
async def login_form(request: Request, dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        cliente = session.query(Cliente).filter(Cliente.id_usuario == usuario.id_usuario).first()
        
        if not cliente:
            raise HTTPException(status_code=400, detail="Cliente não encontrado para este usuário")
        
        access_token = criar_token(usuario.id_usuario)
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "id_cliente": cliente.id_cliente,
            "nome_cliente": cliente.nome
        }


@auth_router.get("/refresh")
@limiter.limit("10/minute")   
async def use_refresh_token(request: Request, usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id_usuario)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
        }