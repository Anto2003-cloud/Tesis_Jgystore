from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Conexión Directa optimizada para Render
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:qjwiN48b1GwamqV4@db.zmfuanfzrrmuztucnzni.supabase.co:5432/postgres"

# El secreto está aquí: añadimos pool_pre_ping para que si la conexión se duerme, se despierte sola
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()