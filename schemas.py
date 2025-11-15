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
    id_contrato: int
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

class ParcelaSchema(BaseModel):
    id_parcela: int
    numero_parcela: int
    valor_parcela: float
    data_vencimento: date
    data_pagamento: Optional[date] = None
    valor_pago: Optional[float] = None
    status: str

    class Config:
        from_attributes = True

class FinanceiroCompletoSchema(BaseModel):
    id_financeiro: int
    valor_total: float
    valor_entrada: float
    taxa_juros: Optional[float] = None
    qtde_parcelas: int
    data_primeiro_vencimento: date
    status_pagamento: str
    data_criacao: date
    parcelas: list[ParcelaSchema] = []

    class Config:
        from_attributes = True

class VeiculoCompletoSchema(BaseModel):
    id_veiculo: int
    marca: str
    modelo: str
    ano_fabricacao: int
    ano_modelo: int
    cor: Optional[str] = None
    placa: Optional[str] = None
    num_chassi: str
    num_renavam: str
    valor: float

    class Config:
        from_attributes = True

class ClienteInfoSchema(BaseModel):
    """Schema com informações básicas do cliente"""
    id_cliente: int
    nome: str
    cpf: str
    email: str
    telefone: Optional[str] = None
    renda: Optional[float] = None

    class Config:
        from_attributes = True

class ContratoCompletoSchema(BaseModel):
    id_contrato: int
    numero_contrato: str
    status: str
    id_cliente: int
    data_emissao: date
    vigencia_fim: Optional[date] = None
    veiculo: VeiculoCompletoSchema
    financeiro: FinanceiroCompletoSchema
    cliente: ClienteInfoSchema  

    class Config:
        from_attributes = True

class InformacoesFipeSchema(BaseModel):
    Valor: Optional[str] = None
    Combustivel: Optional[str] = None
    CodigoFipe: Optional[str] = None  
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
    valorEntrada: Union[float, None] = 0.0  
    parcelasSelecionadas: int
    taxaJuros: float
    rendaMensal: Union[float, None] = 0.0  
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
    marcaSelecionada: Optional[Union[str, int]] = None  
    marcaNome: Optional[str] = None
    modeloSelecionado: Optional[Union[str, int]] = None  
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

        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True
        extra = "ignore"

# ========================
# Schemas para Admin
# ========================

class SolicitacaoListaSchema(BaseModel):
    """Schema para listar solicitações em aberto no painel admin"""
    id_contrato: int
    numero_contrato: str
    id_cliente: int
    nome_cliente: str
    marca_veiculo: str
    modelo_veiculo: str
    valor_veiculo: float
    valor_entrada: float
    qtde_parcelas: int
    status: str
    data_emissao: date

    class Config:
        from_attributes = True

class SolicitacoesResponseSchema(BaseModel):
    """Resposta com lista de solicitações"""
    solicitacoes: list[SolicitacaoListaSchema]
    total: int

    class Config:
        from_attributes = True

class ContratoListaSchema(BaseModel):
    """Schema para listar contratos vigentes no painel admin"""
    id_contrato: int
    numero_contrato: str
    id_cliente: int
    nome_cliente: str
    marca_veiculo: str
    modelo_veiculo: str
    valor_total: float
    status: str
    data_emissao: date

    class Config:
        from_attributes = True

class ContratosVigentesResponseSchema(BaseModel):
    """Resposta com lista de contratos vigentes"""
    contratos: list[ContratoListaSchema]
    total: int

    class Config:
        from_attributes = True

class SolicitacaoDetalheSchema(BaseModel):
    """Schema com detalhes completos de uma solicitação"""
    id_contrato: int
    numero_contrato: str
    id_cliente: int
    nome_cliente: str
    cpf_cliente: str
    email_cliente: str
    telefone_cliente: Optional[str] = None
    data_emissao: date
    status: str
    veiculo: VeiculoCompletoSchema
    financeiro: FinanceiroCompletoSchema

    class Config:
        from_attributes = True

class AprovarRejeitarSchema(BaseModel):
    """Schema para aprovar ou rejeitar solicitação"""
    motivo: Optional[str] = None

    class Config:
        from_attributes = True

class DashboardMetricasSchema(BaseModel):
    """Schema com métricas do dashboard admin"""
    solicitacoes_pendentes: int
    contratos_ativos: int
    valor_total_financiado: float
    parcelas_em_atraso_qtd: int
    parcelas_em_atraso_valor: float

    class Config:
        from_attributes = True  