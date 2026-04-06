from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database
from database import SessionLocal, engine
from datetime import datetime
import httpx
import os

# 1. Inicialización de la Base de Datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jgystore API - Sistema de Gestión Adaptativa")
from fastapi import Form

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Estos son los datos que usará Fran para entrar. Puedes cambiarlos.
USUARIO_ADMIN = "admin"
CLAVE_ADMIN = "Gystore2026" 

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == USUARIO_ADMIN and password == CLAVE_ADMIN:
        return {"status": "success", "message": "Acceso concedido"}
    else:
        raise HTTPException(status_code=401, detail="Usuario o clave incorrectos")
# 2. Permisos CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. ROBOT DE BÚSQUEDA DE TASA (BCV)
async def obtener_tasa_nube():
    urls = [
        "https://ve.dolarapi.com/v1/dolares/oficial",
        "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv"
    ]
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        for url in urls:
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    datos = r.json()
                    valor = datos.get('promedio') or datos.get('value') or datos.get('price')
                    if valor:
                        return float(valor)
            except Exception:
                continue
    return None

# --- RUTA PARA VER LA PÁGINA WEB ---
@app.get("/")
def ver_panel_control():
    return FileResponse('index.html')

# --- RUTA DE PRODUCTOS ---
@app.get("/productos/")
async def obtener_productos(db: Session = Depends(get_db)):
    valor_real = await obtener_tasa_nube()
    if valor_real:
        nueva_tasa = models.Tasa(valor=valor_real, fuente="BCV Oficial")
        db.add(nueva_tasa)
        db.commit()

    ultima_tasa_db = db.query(models.Tasa).order_by(models.Tasa.id.desc()).first()
    tasa_usar = ultima_tasa_db.valor if ultima_tasa_db else 36.50
    
    productos = db.query(models.Producto).all()
    resultado = []
    
    for p in productos:
        pv_usd = p.costo_usd + (p.costo_usd * p.margen_ganancia / 100)
        pv_bs = pv_usd * tasa_usar
        
        if p.stock_actual <= 0:
            alerta = "⚠️ AGOTADO"
        elif p.stock_actual <= p.stock_minimo:
            alerta = "❗ RECOMPRAR"
        else:
            alerta = "✅ DISPONIBLE"
        
        resultado.append({
            "nombre": p.nombre,
            "stock": p.stock_actual,
            "precio_bs": round(pv_bs, 2),
            "tasa_bcv_aplicada": tasa_usar,
            "analisis_inventario": alerta,
            "fecha_actualizacion": datetime.now().strftime("%H:%M:%S")
        })
    return resultado

# --- RUTA PARA CREAR PRODUCTOS ---
@app.post("/productos/")
def crear_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    nuevo_p = models.Producto(
        nombre=producto.nombre,
        categoria=producto.categoria,
        costo_usd=producto.costo_usd,
        margen_ganancia=producto.margen_ganancia,
        stock_actual=producto.stock_actual,
        stock_minimo=producto.stock_minimo
    )
    db.add(nuevo_p)
    db.commit()
    db.refresh(nuevo_p)
    return nuevo_p