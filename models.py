from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    costo_usd = Column(Float, nullable=False)
    margen_ganancia = Column(Float, nullable=False)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

class TasaCambio(Base):
    __tablename__ = "tasa_cambio"
    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)