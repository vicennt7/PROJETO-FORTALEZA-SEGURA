# app/banco_de_dados/db_config.py

import os
from sqlalchemy import create_engine
# ALTERADO: Importando a ferramenta nova e mais específica
from sqlalchemy.orm import sessionmaker, declarative_base 

# String de Conexão com o Banco de Dados
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:*A159357o@localhost:5432/postgres"

# O "Motor" do Banco de Dados
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# A "Agência" de Sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ALTERADO: Usando a "Planta Mestra" com o novo nome recomendado
Base = declarative_base()