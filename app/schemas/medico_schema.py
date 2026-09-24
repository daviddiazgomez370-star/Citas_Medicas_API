from pydantic import BaseModel, EmailStr, field_validator

class MedicoCreate(BaseModel):
    nombre: str
    documento: str
    telefono: str
    email: EmailStr
    password: str
    especialidad: str

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
        
        if len(value) != 10:
            raise ValueError(
                "El documento debe tener 10 números"
            )
        
        return value
    
    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, value):
        if not value.isdigit():
            raise ValueError(
                "El telefono debe contener números"
            )
        
        if len(value) != 10:
            raise ValueError(
                "El teléfono debe tener 10 números"
            )
        
        return value
    
    @field_validator("password")
    @classmethod
    def validar_password(cls, value):
        if len(value) < 6:
            raise ValueError(
                "La contraseña debe tener mínimo 6 caracteres"
            )
        
        return value
    
    @field_validator("especialidad")
    @classmethod
    def validar_especialidad(cls, value):
        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "La especialidad es obligatoria"
            )
        
        return value
    
class MedicoResponse(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    documento: str
    telefono: str
    email: EmailStr
    especialidad: str

    model_config = {
        "from_attributes": True
    }