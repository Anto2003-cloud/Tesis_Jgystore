from fastapi import FastAPI
import models
from database import engine

app = FastAPI(title="Jgystore API")

# Esto crea las tablas físicamente al ejecutar el servidor
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"status": "Sistema Jgystore en línea"}