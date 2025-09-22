# app/banco_de_dados/db_saida.py
import enum
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .db_config import Base

# --- "Etiquetas" de Classificação (Enums Completos e Padronizados) ---
class TipoEvento(enum.Enum):
    CRIME_CONTRA_PESSOA = "crime_contra_pessoa"
    CRIME_CONTRA_PATRIMONIO = "crime_contra_patrimonio"
    ACIDENTE_TRANSITO = "acidente_de_transito"
    INFRAESTRUTURA_URBANA = "infraestrutura_urbana"
    ATIVIDADE_SUSPEITA = "atividade_suspeita"
    RISCO_SANITARIO = "risco_sanitario"
    QUALIDADE_AMBIENTAL = "qualidade_ambiental"
    EVENTO_PUBLICO = "evento_publico"
    ALERTA_CLIMATICO = "alerta_climatico"

class NivelGravidade(enum.Enum):
    INFORMATIVO = "informativo"
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

class TipoPontoInteresse(enum.Enum):
    REFUGIO_SEGURO = "refugio_seguro"
    ORGAO_PUBLICO = "orgao_publico"
    PONTO_DE_LAZER = "ponto_de_lazer"
    GASTRONOMIA_LOCAL = "gastronomia_local"
    CULTURA_ARTE_LOCAL = "cultura_arte_local"
    ZONA_DE_RISCO_CONHECIDA = "zona_de_risco_conhecida"
    LOCAL_DE_EVENTOS = "local_de_eventos"
    PONTO_MONITORAMENTO_PRAIA = "ponto_monitoramento_praia"
    ESTACIONAMENTO_COMERCIAL = "estacionamento_comercial"
    PARADA_ONIBUS = "parada_onibus"
    ESTACAO_METRO = "estacao_metro"
    TERMINAL_INTEGRACAO = "terminal_integracao"

class StatusSessao(enum.Enum):
    ATIVA_EM_ROTA = "ativa_em_rota"
    ALERTA_PANICO = "alerta_panico"
    FINALIZADA = "finalizada"
    CANCELADA_USUARIO = "cancelada_pelo_usuario"

class TipoGatilhoAlerta(enum.Enum):
    BOTAO_PANICO_USUARIO = "botao_panico_usuario"
    ANTI_ROUBO_SISTEMA = "anti_roubo_sistema"

class StatusAlerta(enum.Enum):
    VERIFICACAO_PENDENTE = "verificacao_pendente"
    RASTREAMENTO_ATIVO = "rastreamento_ativo"
    CANCELADO_USUARIO = "cancelado_usuario"
    FINALIZADO_AUTORIDADES_ACIONADAS = "finalizado_autoridades_acionadas"

class NivelFluxo(enum.Enum):
    INEXISTENTE = "inexistente"
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"

class TopologiaVia(enum.Enum):
    AVENIDA = "avenida"
    RUA_LARGA = "rua_larga"
    RUA_ESTREITA = "rua_estreita"
    TRAVESSA = "travessa"
    BECO_VIELA = "beco_viela"

# --- AS PLANTAS DAS TABELAS DE SAÍDA ---
class Bairro(Base):
    __tablename__ = "bairros"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, index=True)
    regional = Column(String, nullable=True)
    populacao_estimada = Column(Integer, nullable=True)
    idhm = Column(Float, nullable=True)
    geometria_area = Column(Geometry('POLYGON', srid=4326), nullable=True)
    eventos = relationship("Evento", back_populates="bairro")
    segmentos_de_via = relationship("SegmentoDeVia", back_populates="bairro")

class Evento(Base):
    __tablename__ = "eventos_seguranca"
    id = Column(Integer, primary_key=True)
    id_dado_bruto = Column(Integer, index=True, nullable=True)
    link_fonte = Column(String, unique=True, index=True)
    titulo = Column(String)
    resumo = Column(Text, nullable=True)
    tipo_evento = Column(Enum(TipoEvento), index=True)
    subtipo_evento = Column(String, nullable=True)
    nivel_gravidade = Column(Enum(NivelGravidade), index=True)
    data_evento = Column(DateTime, index=True)
    ponto_geografico = Column(Geometry('POINT', srid=4326), index=True)
    bairro_id = Column(Integer, ForeignKey("bairros.id"), nullable=True)
    bairro = relationship("Bairro", back_populates="eventos")

class PontoDeInteresse(Base):
    __tablename__ = "pontos_de_interesse"
    id = Column(Integer, primary_key=True)
    nome = Column(String, index=True)
    tipo = Column(Enum(TipoPontoInteresse), index=True)
    coordenadas = Column(Geometry('POINT', srid=4326), index=True)
    horario_funcionamento = Column(String, nullable=True)
    risco_associado_calculado = Column(Float, default=0.5)

class SegmentoDeVia(Base):
    __tablename__ = "segmentos_de_via"
    id = Column(Integer, primary_key=True)
    nome_rua = Column(String, index=True, nullable=True)
    geometria_linha = Column(Geometry('LINESTRING', srid=4326), index=True)
    bairro_id = Column(Integer, ForeignKey("bairros.id"), nullable=True)
    bairro = relationship("Bairro", back_populates="segmentos_de_via")
    fluxo_pedestres_diurno = Column(Enum(NivelFluxo), default=NivelFluxo.MEDIO)
    fluxo_pedestres_noturno = Column(Enum(NivelFluxo), default=NivelFluxo.MEDIO)
    presenca_comercio_diurno = Column(Boolean, default=False)
    presenca_comercio_noturno = Column(Boolean, default=False)
    presenca_transporte_publico = Column(Boolean, default=False)
    topologia_via = Column(Enum(TopologiaVia), default=TopologiaVia.RUA_LARGA)
    percepcao_iluminacao = Column(Enum("BOA", "MEDIA", "RUIM", name="iluminacao_enum"), default="MEDIA")
    risco_pedestre_calculado = Column(Float, default=0.5, index=True)
    risco_veicular_calculado = Column(Float, default=0.5, index=True)

class SessaoAtiva(Base):
    __tablename__ = "sessoes_ativas"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True)
    data_inicio = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    status = Column(Enum(StatusSessao), default=StatusSessao.ATIVA_EM_ROTA)
    coordenadas_veiculo_estacionado = Column(Geometry('POINT', srid=4326), nullable=True)
    coordenadas_destino_final = Column(Geometry('POINT', srid=4326), nullable=True)

class CaixaPreta(Base):
    __tablename__ = "caixa_preta_alertas"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True)
    sessao_id = Column(Integer, ForeignKey("sessoes_ativas.id"), index=True, nullable=True)
    tipo_gatilho = Column(Enum(TipoGatilhoAlerta), index=True)
    motivo_gatilho_sistema = Column(String, nullable=True)
    status_alerta = Column(Enum(StatusAlerta), index=True)
    data_inicio_alerta = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    data_final_alerta = Column(DateTime, nullable=True)
    verificacao_solicitada = Column(Boolean, default=False)
    verificacao_sucesso = Column(Boolean, nullable=True)
    coordenadas_iniciais = Column(Geometry('POINT', srid=4326))
    historico_rastreamento = Column(JSON, nullable=True)