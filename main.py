ffrom fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine

# Esto crea las tablas en Supabase apenas arranca el programa
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    return templates.TemplateResponse("index.html", {"request": request, "productos": productos})

@app.post("/agregar")
async def agregar_producto(
    nombre: str = Form(...),
    categoria: str = Form(...),
    costo: float = Form(...),
    margen: float = Form(...),
    stock: int = Form(...),
    stock_min: int = Form(...),
    db: Session = Depends(get_db)
):
    nuevo = models.Producto(
        nombre=nombre,
        categoria=categoria,
        costo_usd=costo,
        margen_ganancia=margen,
        stock_actual=stock,
        stock_minimo=stock_min
    )
    db.add(nuevo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/editar/{producto_id}")
async def editar_producto(
    producto_id: int,
    nombre: str = Form(...),
    categoria: str = Form(...),
    costo: float = Form(...),
    margen: float = Form(...),
    stock: int = Form(...),
    stock_min: int = Form(...),
    db: Session = Depends(get_db)
):
    p = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if p:
        p.nombre = nombre
        p.categoria = categoria
        p.costo_usd = costo
        p.margen_ganancia = margen
        p.stock_actual = stock
        p.stock_minimo = stock_min
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/eliminar/{producto_id}")
async def eliminar(producto_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if p:
        db.delete(p)
        db.commit()
    return RedirectResponse(url="/", status_code=303)