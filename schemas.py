from pydantic import BaseModel
from typing import Optional

class TasaCreate(BaseModel):
    valor: float
    fuente: Optional[str] = "Binance P2P"

class ProductoCreate(BaseModel):
    nombre: str
    categoria: str
    costo_usd: float
    margen_ganancia: float
    stock_actual: int
    stock_minimo: int

# ESTA CLASE ES LA QUE HACE QUE SE VEA LA TASA
class ProductoVer(BaseModel):
    nombre: str
    precio_venta_usd: float
    precio_venta_bs: float
    tasa_aplicada: float
    stock: int