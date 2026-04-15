from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Este es el link optimizado para evitar el error "Network is unreachable"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.zmfuanfzrrmuztucnzni:qjwiN48b1GwamqV4@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()