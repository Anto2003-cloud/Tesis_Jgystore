from fastapi import FastAPI, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from typing import List

# Crea las tablas en Neon automáticamente si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración de plantillas
templates = Jinja2Templates(directory="templates")

# Dependencia para obtener la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    tasa_obj = db.query(models.TasaDolar).first()
    tasa = tasa_obj.valor if tasa_obj else 0.0
    
    # Calculamos los precios en bolívares para cada producto
    for producto in productos:
        producto.precio_bs = producto.precio_dolar * tasa
        
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "productos": productos, 
        "tasa": tasa
    })

@app.post("/agregar")
def agregar_producto(
    nombre: str = Form(...),
    categoria: str = Form(...),
    costo: float = Form(...),
    margen: float = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db)
):
    # Cálculo simple del precio en dólares basado en margen
    precio_dolar = costo * (1 + (margen / 100))
    nuevo_producto = models.Producto(
        nombre=nombre,
        categoria=categoria,
        costo=costo,
        margen=margen,
        precio_dolar=precio_dolar,
        stock=stock
    )
    db.add(nuevo_producto)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/actualizar_tasa")
def actualizar_tasa(tasa: float = Form(...), db: Session = Depends(get_db)):
    tasa_obj = db.query(models.TasaDolar).first()
    if tasa_obj:
        tasa_obj.valor = tasa
    else:
        tasa_obj = models.TasaDolar(valor=tasa)
        db.add(tasa_obj)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/eliminar/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto:
        db.delete(producto)
        db.commit()
    return RedirectResponse(url="/", status_code=303)