"""
database.py - Configuración de base de datos para SIGPIA
Conexión a PostgreSQL
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# ── Variables de entorno ───────────────────────────────────────────────────────
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "sigpia")

# ── URL de conexión ────────────────────────────────────────────────────────────
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)

# ── Engine ─────────────────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    echo=False,          # Cambiar a True para ver SQL generado en consola
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
    pool_recycle=3600,   # Recicla conexiones cada hora
)

# ── SessionLocal ───────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ── Base declarativa ───────────────────────────────────────────────────────────
Base = declarative_base()


# ── Dependencia para FastAPI ───────────────────────────────────────────────────
def get_db():
    """
    Generador de sesión de base de datos para usar como dependencia en FastAPI.

    Uso:
        @router.get("/ejemplo")
        def ejemplo(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()