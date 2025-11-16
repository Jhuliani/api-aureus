from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from models import db
from sqlalchemy.orm import sessionmaker, Session
from models import Usuario
from jose import jwt, JWTError

def pegar_sessao():
    SessionLocal = sessionmaker(bind=db, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = dic_info.get("sub")
    except JWTError as erro:
        print(erro)
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    usuario = session.query(Usuario).filter(Usuario.id_usuario==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return usuario

def verificar_admin(usuario: Usuario = Depends(verificar_token)):
    if usuario.id_perfil != 2:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem acessar esta rota.")
    return usuario