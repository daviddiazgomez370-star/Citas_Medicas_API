from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UsuarioActualResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str