from fastapi import FastAPI, Depends, Form, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database
from database import SessionLocal, engine
from datetime import datetime
import httpx

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jgystore - Sistema de Gestión")

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
    url = "https://ve.dolarapi.com/v1/dolares/oficial"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url)
            if r.status_code == 200:
                datos = r.json()
                return float(datos.get('promedio') or datos.get('price'))
        except:
            pass
    return None

@app.get("/")
def ver_panel_control():
    return FileResponse('index.html')

@app.get("/productos")
async def obtener_productos(db: Session = Depends(get_db)):
    tasa_api = await obtener_tasa_nube()
    if tasa_api:
        nueva = models.Tasa(valor=tasa_api, fuente="BCV", fecha=datetime.now())
        db.add(nueva)
        db.commit()
    
    tasa_db = db.query(models.Tasa).order_by(models.Tasa.id.desc()).first()
    tasa = tasa_db.valor if tasa_db else 36.50
    
    productos = db.query(models.Producto).all()
    res = []
    for p in productos:
        pv_usd = p.costo_usd + (p.costo_usd * (p.margen_ganancia / 100))
        res.append({
            "id": p.id,
            "nombre": p.nombre,
            "stock": p.stock_actual,
            "ref_usd": round(pv_usd, 2),
            "precio_bs": round(pv_usd * tasa, 2),
            "estado": "✅ DISPONIBLE" if p.stock_actual > 5 else "❗ RECOMPRAR"
        })
    
    return {
        "productos": res,
        "tasa_actual": tasa,
        "total_productos": len(res),
        "alertas": len([p for p in productos if p.stock_actual <= 5])
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
        nombre=nombre, categoria="General", costo_usd=costo, 
        margen_ganancia=margen, stock_actual=stock, stock_minimo=5
    )
    db.add(nuevo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- NUEVA FUNCIÓN PARA ELIMINAR ---
@app.post("/eliminar-producto/{producto_id}")
async def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto:
        db.delete(producto)
        db.commit()
    return RedirectResponse(url="/", status_code=303)