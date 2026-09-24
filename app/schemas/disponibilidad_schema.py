from datetime import date, time

from pydantic import BaseModel, model_validator

class DisponibilidadCreate(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: time

    @model_validator(mode="after")
    def validar_disponibilidad(self):
        if self.fecha < date.today():
            raise ValueError(
                "La fecha de disponibilidad no puede estar en el pasado"
            )
        
        if self.hora_fin <= self.hora_inicio:
            raise ValueError(
                "La hora final debe ser posterior a la hora inicial "
            )
        
        return self
    
class DisponibilidadUpdate(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: time

    @model_validator(mode="after")
    def validar_disponibilidad(self):
        if self.fecha < date.today():
            raise ValueError(
                "La fecha de disponibilidad no puede estar en el pasado"
            )
        
        if self.hora_fin <= self.hora_inicio:
            raise ValueError(
                "La hora final debe ser posterior a la hoa inicial"
            )
        
        return self
    
class DisponibilidadResponse(BaseModel):
    id: int
    medico_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time

    model_config = {
        "from_attributes": True
    }