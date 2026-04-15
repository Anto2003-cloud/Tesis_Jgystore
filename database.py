from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Link optimizado para el Pooler de Supabase
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.zmfuanfzrrmuztucnzni:qjwiN48b1GwamqV4@aws-0-us-west-2.pooler.supabase.com:6543/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()