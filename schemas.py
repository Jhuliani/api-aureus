from pydantic import BaseModel
from typing import Optional

class SimulacaoSchema(BaseModel):
    valor_veiculo: float
    valor_entrada:  float
    numero_parcelas: int
    taxa_juros: float
    renda_mensal: float

    class Config:
        from_attributes = True

class SolicitacaoSchema(BaseModel):
    valor_veiculo: float
    valor_entrada:  float
    numero_parcelas: int
    taxa_juros: float
    renda_mensal: float

    class Config:
        from_attributes = True


    class Config:
        from_attributes = True

class UsuarioSchema(BaseModel):
    login:  str
    senha: str 
    id_perfil: int

    class Config:
        from_attributes = True
    

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True