from fastapi import FastAPI, Depends, Form, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database
from database import SessionLocal, engine
from datetime import datetime
import httpx

# Inicialización de la Base de Datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gystore - Sistema de Gestión")

# Seguridad (Mantenemos tus credenciales)
USUARIO_ADMIN = "admin"
CLAVE_ADMIN = "Gystore2026"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def obtener_tasa_nube():
    # Usamos la API de DolarApi para Venezuela (BCV)
    url = "https://ve.dolarapi.com/v1/dolares/oficial"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url)
            if r.status_code == 200:
                datos = r.json()
                # Intentamos obtener el valor del promedio o price
                return float(datos.get('promedio') or datos.get('price'))
        except Exception as e:
            print(f"Error obteniendo tasa: {e}")
    return None

@app.get("/")
def ver_panel_control():
    return FileResponse('index.html')

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == USUARIO_ADMIN and password == CLAVE_ADMIN:
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@app.get("/productos/")
async def obtener_productos(db: Session = Depends(get_db)):
    # 1. Intentamos actualizar la tasa desde la nube
    tasa_api = await obtener_tasa_nube()
    if tasa_api:
        nueva_tasa = models.Tasa(valor=tasa_api, fuente="BCV", fecha=datetime.now())
        db.add(nueva_tasa)
        db.commit()
    
    # 2. Buscamos la última tasa guardada o usamos una por defecto
    tasa_db = db.query(models.Tasa).order_by(models.Tasa.id.desc()).first()
    tasa = tasa_db.valor if tasa_db else 36.50
    
    # 3. Consultamos los productos
    productos = db.query(models.Producto).all()
    res = []
    for p in productos:
        # Cálculo del precio adaptativo (Costo + Margen)
        pv_usd = p.costo_usd + (p.costo_usd * (p.margen_ganancia / 100))
        res.append({
            "id": p.id,
            "nombre": p.nombre,
            "stock": p.stock_actual,
            "ref_usd": round(pv_usd, 2),
            "precio_bs": round(pv_usd * tasa, 2),
            "estado": "✅ DISPONIBLE" if p.stock_actual > p.stock_minimo else "❗ RECOMPRAR"
        })
    
    # Enviamos tanto la lista como la tasa para que el JS no falle
    return {
        "productos": res,
        "tasa_actual": tasa,
        "total_productos": len(res),
        "alertas": len([p for p in productos if p.stock_actual <= p.stock_minimo])
    }

@app.post("/crear-producto-web")
async def crear_web(
    nombre: str = Form(...), 
    costo: float = Form(...), 
    margen: float = Form(...), 
    stock: int = Form(...),
    db: Session = Depends(get_db)
):
    nuevo = models.Producto(
        nombre=nombre, 
        categoria="General", 
        costo_usd=costo, 
        margen_ganancia=margen, 
        stock_actual=stock, 
        stock_minimo=5
    )
    db.add(nuevo)
    db.commit()
    # Redirigimos al inicio para que el usuario vea el cambio de inmediato
    return RedirectResponse(url="/", status_code=303)