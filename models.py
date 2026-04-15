from sqlalchemy import Column, Integer, String, Float
from database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    costo_usd = Column(Float, nullable=False)
    margen_ganancia = Column(Float, nullable=False)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)

class Tasa(Base):
    __tablename__ = "tasas"
    id = Column(Integer, primary_key=True, index=True)
    fuente = Column(String, default="Binance P2P")
    valor = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)