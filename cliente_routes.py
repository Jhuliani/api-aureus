from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import SimulacaoSchema, SolicitacaoSchema
from models import Contrato


cliente_router = APIRouter(prefix="/cliente", tags=["cliente"], dependencies=[Depends(verificar_token)])

@cliente_router.get("/contratos/{id_user}")
async def contratos(id_user, session: Session = Depends(pegar_sessao)):
    contratos = session.query(Contrato).filter(Contrato.id_user==id_user).first()
    session.add(contratos)
    session.commit()
    return {
            "contratos": contratos
        }
