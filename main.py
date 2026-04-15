from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine

# ESTA LÍNEA CREA LAS TABLAS EN SUPABASE AUTOMÁTICAMENTE
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
    tasa_obj = db.query(models.TasaCambio).order_by(models.TasaCambio.id.desc()).first()
    valor_tasa = tasa_obj.valor if tasa_obj else 36.0
    return templates.TemplateResponse("index.html", {"request": request, "productos": productos, "tasa": valor_tasa})

@app.post("/agregar")
async def agregar(nombre:str=Form(...), categoria:str=Form(...), costo:float=Form(...), margen:float=Form(...), stock:int=Form(...), stock_min:int=Form(...), db:Session=Depends(get_db)):
    nuevo = models.Producto(nombre=nombre, categoria=categoria, costo_usd=costo, margen_ganancia=margen, stock_actual=stock, stock_minimo=stock_min)
    db.add(nuevo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/tasa")
async def actualizar_tasa(valor: float = Form(...), db: Session = Depends(get_db)):
    nueva = models.TasaCambio(valor=valor)
    db.add(nueva)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/eliminar/{p_id}")
async def eliminar(p_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Producto).filter(models.Producto.id == p_id).first()
    if p:
        db.delete(p)
        db.commit()
    return RedirectResponse(url="/", status_code=303)