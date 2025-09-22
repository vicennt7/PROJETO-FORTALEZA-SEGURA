# app/banco_de_dados/create_all_tables.py

# --- 1. Importa as ferramentas de base ---
# Acessamos nosso arquivo de configuração para pegar o "motor" (engine)
# e a "planta mestra" (Base)
from .db_config import engine, Base

# --- 2. Importa TODAS as nossas "plantas" de tabelas ---
# Ao importar as classes das tabelas, o Python "aprende" sobre elas e
# as registra na nossa "planta mestra" (Base).
from .db_entrada import Usuario, DadoBruto
from .db_saida import Bairro, Evento, PontoDeInteresse, SegmentoDeVia, SessaoAtiva, CaixaPreta

print("-> Preparando para construir a fundação da Central de Inteligência no PostGIS...")

# --- 3. O Comando de Construção ---
# Esta é a ordem final. Ela diz ao SQLAlchemy:
# "Pegue todas as plantas registradas na 'Base' e crie as tabelas no
# banco de dados ao qual o 'engine' está conectado."
Base.metadata.create_all(bind=engine)

print("✅ FUNDAÇÃO CONSTRUÍDA! Todas as tabelas foram criadas/atualizadas com sucesso.")