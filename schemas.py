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

class InformacoesFipeSchema(BaseModel):
    Valor: Optional[str] = None
    Combustivel: Optional[str] = None
    CodigoFIPE: Optional[str] = None
    MesReferencia: Optional[str] = None

    class Config:
        from_attributes = True

class VeiculoSchema(BaseModel):
    placa: str
    numChassi: str
    numRenavam: str
    cor: Optional[str] = None

    class Config:
        from_attributes = True

class FinanceiroSchema(BaseModel):
    valorVeiculo: float
    valorEntrada: float
    parcelasSelecionadas: int
    taxaJuros: float
    rendaMensal: float
    valorFinanciado: Optional[float] = None
    valorParcela: Optional[float] = None
    totalPagar: Optional[float] = None
    totalJuros: Optional[float] = None

    class Config:
        from_attributes = True

class SolicitacaoCompletaSchema(BaseModel):
    id_cliente: int
    informacoesFipe: Optional[InformacoesFipeSchema] = None
    tipoVeiculo: Optional[str] = None
    marcaSelecionada: Optional[str] = None
    marcaNome: Optional[str] = None
    modeloSelecionado: Optional[str] = None
    modeloNome: Optional[str] = None
    anoSelecionado: Optional[str] = None
    veiculo: VeiculoSchema
    financeiro: FinanceiroSchema

    class Config:
        from_attributes = True