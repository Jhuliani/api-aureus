from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token


admin_router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verificar_token)])