from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator

class UsuarioCreate(BaseModel):
    nombre: str
    documento: str
    telefono: str
    email: EmailStr
    password: str
    rol: Literal["paciente", "medico"]

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value):
        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "El nombre debe tener mínimo 3 caracteres"
            )
        
        return value
    
    @field_validator("documento")
    @classmethod
    def validar_documento(cls, value):
        if not value.isdigit():
            raise ValueError(
                "El documento solo debe contener números"
            )
        
        if len(value) < 6 or len(value) > 15:
            raise ValueError(
                "El documento debe tener entre 6 y 15 números"
            )
        
        return value
    
    # @field_validator()