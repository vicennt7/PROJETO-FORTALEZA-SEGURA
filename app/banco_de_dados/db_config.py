# app/banco_de_dados/db_config.py
import os
from pathlib import Path
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Carrega .env se quiser (opcional se já usa python-dotenv em outro lugar) ---
try:
    from dotenv import load_dotenv
    # tenta achar um .env na raiz do projeto
    here = Path(__file__).resolve()
    candidates = [here.parents[2] / ".env", here.parents[1] / ".env", here.parent / ".env"]
    for c in candidates:
        if c.exists():
            load_dotenv(c)
            break
except Exception:
    pass

DB_ENGINE = (os.getenv("DB_ENGINE") or "sqlite").strip().lower()

if DB_ENGINE == "sqlite":
    # Caminho do arquivo do SQLite
    sqlite_path = os.getenv("SQLITE_PATH") or "./app.db"
    sqlite_path = Path(sqlite_path).resolve()
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{sqlite_path}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    missing = [k for k, v in {
        "DB_USER": DB_USER, "DB_PASSWORD": DB_PASSWORD,
        "DB_HOST": DB_HOST, "DB_PORT": DB_PORT, "DB_NAME": DB_NAME
    }.items() if not v]
    if missing:
        raise ValueError("ERRO CRÍTICO: Variáveis ausentes no .env: " + ", ".join(missing))

    DB_USER = quote_plus(DB_USER)
    DB_PASSWORD = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
