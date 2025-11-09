from pydantic import BaseModel, field_validator
from typing import Optional, Union
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
    CodigoFipe: Optional[str] = None  # Corrigido: estava CodigoFIPE
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
    valorEntrada: Union[float, None] = 0.0  # Aceita None e converte para 0
    parcelasSelecionadas: int
    taxaJuros: float
    rendaMensal: Union[float, None] = 0.0  # Aceita None e converte para 0
    valorFinanciado: Optional[float] = None
    valorParcela: Optional[float] = None
    totalPagar: Optional[float] = None
    totalJuros: Optional[float] = None

    @field_validator('valorEntrada', 'rendaMensal', mode='before')
    @classmethod
    def converter_none_para_zero(cls, v):
        return v if v is not None else 0.0

    class Config:
        from_attributes = True

class SolicitacaoCompletaSchema(BaseModel):
    id_cliente: int
    informacoesFipe: Optional[InformacoesFipeSchema] = None
    tipoVeiculo: Optional[str] = None
    marcaSelecionada: Optional[Union[str, int]] = None  # Aceita string ou int
    marcaNome: Optional[str] = None
    modeloSelecionado: Optional[Union[str, int]] = None  # Aceita string ou int (frontend envia número)
    modeloNome: Optional[str] = None
    anoSelecionado: Optional[str] = None
    veiculo: VeiculoSchema
    financeiro: FinanceiroSchema
    # Campos extras que podem vir do frontend (ignorados)
    resultadoSimulacao: Optional[dict] = None
    veioDaSimulacao: Optional[bool] = None

    @field_validator('modeloSelecionado', 'marcaSelecionada', mode='before')
    @classmethod
    def converter_para_string(cls, v):
        # Converte número para string se necessário
        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True
        extra = "ignore"  # Ignora campos extras que não estão no schema