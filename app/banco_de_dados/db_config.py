# app/banco_de_dados/db_config.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Passo 1: Carrega as variáveis do arquivo .env para o ambiente do sistema
load_dotenv()

# --- SEÇÃO DE SEGURANÇA ---
# Passo 2: Busca as credenciais de forma segura a partir das variáveis de ambiente
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Validação para garantir que as variáveis foram carregadas com sucesso
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("ERRO CRÍTICO: Uma ou mais variáveis de ambiente do banco de dados não foram definidas no arquivo .env. O programa será encerrado.")

# Passo 3: Monta a string de conexão usando as variáveis seguras
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# --- FIM DA SEÇÃO DE SEGURANÇA ---

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()