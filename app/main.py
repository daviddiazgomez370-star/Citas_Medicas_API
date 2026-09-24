from fastapi import FastAPI

from app.database import Base, engine
from app.database_migrations import migrar_esquema_legacy

from app.models.usuario import Usuario
from app.models.medico_models import Medico
from app.models.disponibilidad import Disponibilidad
from app.models.cita import Cita

from app.routers import (
    auth,
    citas,
    disponibilidad,
    medicos,
    pacientes
)

Base.metadata.create_all(bind=engine)
migrar_esquema_legacy(engine)

app = FastAPI(
    title="Sistema de Gestión de Citas Médicas",
    description="API para gestionar pacientes, médicos, disponibilidad y citas.",
    version="1.0.0"
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Autenticación"]
)

app.include_router(
    pacientes.router,
    prefix="/pacientes",
    tags=["Pacientes"]
)

app.include_router(
    medicos.router,
    prefix="/medicos",
    tags=["Médicos"]
)

app.include_router(
    disponibilidad.router,
    prefix="/disponibilidad",
    tags=["Disponibilidad"]
)

app.include_router(
    citas.router,
    prefix="/Cita",
    tags=["Citas"]
)

@app.get("/")
def inicio():
    return{
        "mensaje": "API de citas médicas funcionando correctamente"
    }
