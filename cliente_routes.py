from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from main import limiter
from schemas import (
    SimulacaoSchema, SolicitacaoSchema, 
    EnderecoCreateSchema, EnderecoResponseSchema,
    UsuarioCreateSchema, UsuarioResponseSchema,
    ClienteCreateSchema, ClienteResponseSchema,
    ClienteCompletoSchema, ContratoDetalhadoSchema, ContratosResponseSchema
)
from models import Contrato, Endereco, Usuario, Cliente, Financeiro
from main import bcrypt_context
from datetime import date

cliente_router = APIRouter(prefix="/cliente", tags=["cliente"])


@cliente_router.post("/endereco", response_model=EnderecoResponseSchema)
@limiter.limit("10/minute")  # Máximo 10 endereços por minuto por IP
async def criar_endereco(
    request: Request,
    endereco_data: EnderecoCreateSchema, 
    session: Session = Depends(pegar_sessao)
):
    """
    Cria um novo endereço e retorna o ID do endereço criado
    """
    try:
        # Criar novo endereço
        novo_endereco = Endereco(
            logradouro=endereco_data.logradouro,
            numero=endereco_data.numero,
            bairro=endereco_data.bairro,
            cidade=endereco_data.cidade,
            estado=endereco_data.estado,
            cep=endereco_data.cep
        )
        
        session.add(novo_endereco)
        session.commit()
        session.refresh(novo_endereco)
        
        return novo_endereco
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar endereço: {str(e)}")


@cliente_router.post("/usuario", response_model=UsuarioResponseSchema)
@limiter.limit("5/minute")  # Máximo 5 usuários por minuto por IP
async def criar_usuario(
    request: Request,
    usuario_data: UsuarioCreateSchema, 
    session: Session = Depends(pegar_sessao)
):
    """
    Cria um novo usuário e retorna o ID do usuário criado
    """
    try:
        # Verificar se login já existe
        usuario_existente = session.query(Usuario).filter(Usuario.login == usuario_data.login).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail="Login já cadastrado")
        
        # Criptografar senha usando bcrypt diretamente
        import bcrypt
        senha_bytes = usuario_data.senha.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode('utf-8')
        
        # Criar novo usuário
        novo_usuario = Usuario(
            id_perfil=usuario_data.id_perfil,
            login=usuario_data.login,
            senha_hash=senha_hash,
            data_criacao=date.today()
        )
        
        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)
        
        return novo_usuario
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar usuário: {str(e)}")


@cliente_router.post("/cliente", response_model=ClienteResponseSchema)
@limiter.limit("5/minute")  # Máximo 5 clientes por minuto por IP
async def criar_cliente(
    request: Request,
    cliente_data: ClienteCreateSchema, 
    session: Session = Depends(pegar_sessao)
):
    """
    Cria um novo cliente usando os IDs do usuário e endereço previamente criados
    """
    try:
        # Verificar se usuário existe
        usuario = session.query(Usuario).filter(Usuario.id_usuario == cliente_data.id_usuario).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se endereço existe
        endereco = session.query(Endereco).filter(Endereco.id_endereco == cliente_data.id_endereco).first()
        if not endereco:
            raise HTTPException(status_code=404, detail="Endereço não encontrado")
        
        # Verificar se CPF já existe
        cliente_existente = session.query(Cliente).filter(Cliente.cpf == cliente_data.cpf).first()
        if cliente_existente:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
        
        # Verificar se email já existe
        email_existente = session.query(Cliente).filter(Cliente.email == cliente_data.email).first()
        if email_existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        # Criar novo cliente
        novo_cliente = Cliente(
            id_usuario=cliente_data.id_usuario,
            id_endereco=cliente_data.id_endereco,
            nome=cliente_data.nome,
            cpf=cliente_data.cpf,
            email=cliente_data.email,
            telefone=cliente_data.telefone,
            renda=cliente_data.renda,
            data_cadastro=date.today()
        )
        
        session.add(novo_cliente)
        session.commit()
        session.refresh(novo_cliente)
        
        return novo_cliente
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar cliente: {str(e)}")


@cliente_router.post("/cadastro-completo")
@limiter.limit("3/minute")  # Máximo 3 cadastros completos por minuto por IP
async def cadastrar_cliente_completo(
    request: Request,
    dados: ClienteCompletoSchema,
    session: Session = Depends(pegar_sessao)
):
    """
    Cadastra cliente completo (endereço + usuário + cliente) em uma única transação
    """
    try:
        # TUDO DENTRO DE UMA TRANSAÇÃO
        session.begin()
        
        # 1. Verificar se login já existe
        usuario_existente = session.query(Usuario).filter(Usuario.login == dados.login).first()
        if usuario_existente:
            session.rollback()
            raise HTTPException(status_code=400, detail="Login já cadastrado")
        
        # 2. Verificar se CPF já existe
        cliente_existente = session.query(Cliente).filter(Cliente.cpf == dados.cpf).first()
        if cliente_existente:
            session.rollback()
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
        
        # 3. Verificar se email já existe
        email_existente = session.query(Cliente).filter(Cliente.email == dados.email).first()
        if email_existente:
            session.rollback()
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        # 4. Criar endereço
        endereco = Endereco(
            logradouro=dados.logradouro,
            numero=dados.numero,
            bairro=dados.bairro,
            cidade=dados.cidade,
            estado=dados.estado,
            cep=dados.cep
        )
        session.add(endereco)
        session.flush()  # Pega o ID sem commit
        
        # 5. Criptografar senha
        import bcrypt
        senha_bytes = dados.senha.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode('utf-8')
        
        # 6. Criar usuário
        usuario = Usuario(
            id_perfil=dados.id_perfil,
            login=dados.login,
            senha_hash=senha_hash,
            data_criacao=date.today()
        )
        session.add(usuario)
        session.flush()  # Pega o ID sem commit
        
        # 7. Criar cliente
        cliente = Cliente(
            id_usuario=usuario.id_usuario,
            id_endereco=endereco.id_endereco,
            nome=dados.nome,
            cpf=dados.cpf,
            email=dados.email,
            telefone=dados.telefone,
            renda=dados.renda,
            data_cadastro=date.today()
        )
        session.add(cliente)
        
        # COMMIT DE TUDO JUNTO
        session.commit()
        
        return {
            "success": True, 
            "id_cliente": cliente.id_cliente,
            "id_usuario": usuario.id_usuario,
            "id_endereco": endereco.id_endereco,
            "message": "Cliente cadastrado com sucesso"
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()  # DESFAZ TUDO SE DER ERRO
        raise HTTPException(status_code=400, detail=f"Erro no cadastro completo: {str(e)}")


@cliente_router.get("/contratos/{id_cliente}", response_model=ContratosResponseSchema, dependencies=[Depends(verificar_token)])
async def contratos(id_cliente: int, session: Session = Depends(pegar_sessao)):
    """
    Retorna informações detalhadas de TODOS os contratos do cliente:
    - Número do Contrato
    - Status
    - ID Cliente
    - ID Veículo
    - ID Financeiro
    - Data Emissão
    """
    # Buscar TODOS os contratos do cliente
    contratos = session.query(Contrato).filter(Contrato.id_cliente == id_cliente).all()
    
    if not contratos:
        raise HTTPException(status_code=404, detail="Nenhum contrato encontrado para este cliente")
    
    # Lista para armazenar os contratos detalhados
    contratos_detalhados = []
    
    # Para cada contrato, buscar dados financeiros e montar resposta
    for contrato in contratos:
        # Buscar dados financeiros relacionados
        financeiro = session.query(Financeiro).filter(Financeiro.id_contrato == contrato.id_contrato).first()
        
        if financeiro:  # Só incluir se tiver dados financeiros
            contrato_detalhado = ContratoDetalhadoSchema(
                numero_contrato=contrato.num_contrato,
                status=contrato.status,
                id_cliente=contrato.id_cliente,
                id_veiculo=contrato.id_veiculo,
                id_financeiro=financeiro.id_financeiro,
                data_emissao=contrato.data_emissao
            )
            contratos_detalhados.append(contrato_detalhado)
    
    if not contratos_detalhados:
        raise HTTPException(status_code=404, detail="Nenhum contrato com dados financeiros encontrado para este cliente")
    
    return ContratosResponseSchema(
        contratos=contratos_detalhados,
        total=len(contratos_detalhados)
    )
