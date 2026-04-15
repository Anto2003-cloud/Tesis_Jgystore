from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Hemos añadido '-pooler' después del ID del endpoint
# Esto fuerza a Neon a usar la ruta más estable y compatible con Render
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_A7Xn2cSJZOhQ@ep-royal-thunder-akkujxva-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()