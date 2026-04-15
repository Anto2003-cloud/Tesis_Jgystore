from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String)
    costo_usd = Column(Float, nullable=False)
    margen_ganancia = Column(Float, default=30.0)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=2)

class Tasa(Base):
    __tablename__ = "tasas"
    id = Column(Integer, primary_key=True, index=True)
    fuente = Column(String, default="Binance P2P")
    valor = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)