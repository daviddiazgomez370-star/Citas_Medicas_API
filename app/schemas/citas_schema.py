from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

class Citacreate(BaseModel):
    medico_id: int
    fecha: date
    hora: time
    motivo: str

    @field_validator("motivo")
    @classmethod
    def validar_motivo(cls, value):
        value = value.strip()

        if len(value) < 5:
            raise ValueError(
                "El motivo debe tener mínimo 5 caracteres"
            )
        
        return value

    @model_validator(mode="after")
    def validar_fecha_hora(self):
        fecha_hora_cita = datetime.combine(
            self.fecha,
            self.hora
        )

        if fecha_hora_cita <= datetime.now():
            raise ValueError(
                "La cita no puede programarse en el pasado"
            )
        
        return self 
    
class CitaResponse(BaseModel):
    id: int
    paciente_id: int
    medico_id: int
    fecha: date
    hora: time
    motivo: str
    estado: str

    model_config = {
        "from_attributes": True
    }
    

class EstadoCitaUpdate(BaseModel):
    estado: Literal[
        "pendiente",
        "confirmada",
        "cancelada"
    ]
