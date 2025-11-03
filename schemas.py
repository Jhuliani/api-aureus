from pydantic import BaseModel
from typing import Optional
from datetime import date

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

class UsuarioSchema(BaseModel):
    login:  str
    senha: str 
    id_perfil: int

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    login: str
    senha: str

    class Config:
        from_attributes = True

class ClienteCompletoSchema(BaseModel):
    # Dados pessoais
    nome: str
    cpf: str
    email: str
    telefone: Optional[str] = None
    renda: Optional[float] = None
    
    # Endereço
    logradouro: str
    numero: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str
    
    # Usuário
    login: str
    senha: str
    id_perfil: int = 2  # Assumindo que 2 é o perfil de cliente

    class Config:
        from_attributes = True

class ContratoDetalhadoSchema(BaseModel):
    numero_contrato: str
    status: str
    id_cliente: int
    id_veiculo: int
    id_financeiro: int
    data_emissao: date

    class Config:
        from_attributes = True

class ContratosResponseSchema(BaseModel):
    contratos: list[ContratoDetalhadoSchema]
    total: int

    class Config:
        from_attributes = True