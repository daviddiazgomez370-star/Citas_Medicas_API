from fastapi import FastAPI

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