from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Nueva URL usando el Pooler de Supabase (más estable para Render)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.zmfuanfzrrmuztucnzni:qjwiN48b1GwamqV4@aws-0-us-west-2.pooler.supabase.com:6543/postgres?sslmode=require"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()