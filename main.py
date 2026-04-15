from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine

# Crea las tablas automáticamente al iniciar
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
def read_root(request: Request, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    tasa_obj = db.query(models.TasaDolar).first()
    tasa = tasa_obj.valor if tasa_obj else 0.0
    for p in productos:
        p.precio_bs = p.precio_dolar * tasa
    return templates.TemplateResponse("index.html", {"request": request, "productos": productos, "tasa": tasa})

@app.post("/agregar")
def agregar(nombre:str=Form(...), categoria:str=Form(...), costo:float=Form(...), margen:float=Form(...), stock:int=Form(...), db:Session=Depends(get_db)):
    p_dolar = costo * (1 + (margen/100))
    nuevo = models.Producto(nombre=nombre, categoria=categoria, costo=costo, margen=margen, precio_dolar=p_dolar, stock=stock)
    db.add(nuevo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/actualizar_tasa")
def actualizar_tasa(tasa:float=Form(...), db:Session=Depends(get_db)):
    obj = db.query(models.TasaDolar).first()
    if obj: obj.valor = tasa
    else: db.add(models.TasaDolar(valor=tasa))
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/eliminar/{id}")
def eliminar(id:int, db:Session=Depends(get_db)):
    p = db.query(models.Producto).filter(models.Producto.id == id).first()
    if p:
        db.delete(p)
        db.commit()
    return RedirectResponse(url="/", status_code=303)