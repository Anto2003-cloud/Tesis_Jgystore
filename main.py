from fastapi import FastAPI, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from datetime import datetime

# Construcción de base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# RUTA PRINCIPAL (Dashboard)
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    # Buscamos la última tasa registrada
    tasa = db.query(models.TasaCambio).order_by(models.TasaCambio.id.desc()).first()
    valor_tasa = tasa.valor if tasa else 1.0
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "productos": productos, 
        "tasa": valor_tasa
    })

# AGREGAR PRODUCTO
@app.post("/agregar")
async def crear(
    nombre: str = Form(...),
    categoria: str = Form(...),
    costo: float = Form(...),
    margen: float = Form(...),
    stock: int = Form(...),
    stock_min: int = Form(...),
    db: Session = Depends(get_db)
):
    nuevo_p = models.Producto(
        nombre=nombre, categoria=categoria, costo_usd=costo,
        margen_ganancia=margen, stock_actual=stock, stock_minimo=stock_min
    )
    db.add(nuevo_p)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# EDITAR PRODUCTO
@app.post("/editar/{p_id}")
async def actualizar(
    p_id: int,
    nombre: str = Form(...),
    categoria: str = Form(...),
    costo: float = Form(...),
    margen: float = Form(...),
    stock: int = Form(...),
    stock_min: int = Form(...),
    db: Session = Depends(get_db)
):
    p = db.query(models.Producto).filter(models.Producto.id == p_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="No encontrado")
    
    p.nombre = nombre
    p.categoria = categoria
    p.costo_usd = costo
    p.margen_ganancia = margen
    p.stock_actual = stock
    p.stock_minimo = stock_min
    
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# ACTUALIZAR TASA (Importante para Punto Fijo)
@app.post("/tasa")
async def actualizar_tasa(valor: float = Form(...), db: Session = Depends(get_db)):
    nueva_tasa = models.TasaCambio(valor=valor)
    db.add(nueva_tasa)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# ELIMINAR
@app.post("/eliminar/{p_id}")
async def borrar(p_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Producto).filter(models.Producto.id == p_id).first()
    if p:
        db.delete(p)
        db.commit()
    return RedirectResponse(url="/", status_code=303)