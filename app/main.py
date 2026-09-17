from fastapi import FastAPI

from app.database import Base, engine
from app.models import usuario

Base.metadata.create_all(bin=engine)

app = FastAPI(
    title="Sistema de Gestión de Citas Médicas",
    description="API para gestionar pacientes, médicos, disponibilidad y citas.",
    version="1.0.0"
)

@app.get("/")
def inicio():
    return{
        "mensaje": "API de citas médicas funcionando correctamente"
    }