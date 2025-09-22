# app/banco_de_dados/db_entrada.py
import enum
import datetime
from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum, DateTime
from .db_config import Base

class FonteDados(enum.Enum):
    NOTICIA_WEB = "noticia_web"
    SOCIAL_MEDIA = "social_media"
    REPORTE_USUARIO = "reporte_de_usuario"
    API_OFICIAL = "api_oficial"

class StatusProcessamento(enum.Enum):
    PENDENTE = "pendente"
    EM_PROCESSAMENTO = "em_processamento"
    PROCESSADO = "processado"
    ERRO = "erro"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome_completo = Column(String, nullable=True)
    nome_usuario = Column(String, unique=True, index=True, nullable=True)
    cpf = Column(String, unique=True, index=True)
    telefone = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email_verificado = Column(Boolean, default=False)
    telefone_verificado = Column(Boolean, default=False)
    url_imagem_perfil = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    data_atualizacao = Column(DateTime, onupdate=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=True)
    ativo = Column(Boolean, default=True, index=True)

class DadoBruto(Base):
    __tablename__ = "dados_brutos"
    id = Column(Integer, primary_key=True)
    fonte = Column(Enum(FonteDados), nullable=False, index=True)
    dados_brutos = Column(JSON)
    status = Column(Enum(StatusProcessamento), default=StatusProcessamento.PENDENTE, index=True)
    link_original = Column(String, unique=True, index=True, nullable=True)
    data_publicacao = Column(DateTime, index=True, nullable=True)
    data_recebimento = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    id_usuario_reporte = Column(Integer, nullable=True)