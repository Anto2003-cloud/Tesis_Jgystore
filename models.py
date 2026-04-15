from sqlalchemy import Column, Integer, String, Float
from database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    categoria = Column(String)
    costo = Column(Float)
    margen = Column(Float)
    precio_dolar = Column(Float)
    stock = Column(Integer)

class TasaDolar(Base):
    __tablename__ = "tasa_dolar"

    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float)