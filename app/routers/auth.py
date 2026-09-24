from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    crear_access_token,
    hash_password,
    password_requiere_migracion,
    verificar_password
)
from app.database import get_db
from app.dependencies.auth import obtener_usuario_actual
from app.models.usuario import Usuario
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UsuarioActualResponse
)

router = APIRouter()

@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"description": "Correo o contraseña incorrectos"}
    }
)
def login(
    datos: LoginRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.email == datos.email
    ).first()

    if usuario is None: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )
    
    migrar_password = password_requiere_migracion(
        usuario.password
    )

    password_correcto = verificar_password(
        datos.password,
        usuario.password
    )

    if not password_correcto:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    if migrar_password:
        usuario.password = hash_password(datos.password)
        db.commit()
    
    token = crear_access_token(
        usuario_id=usuario.id,
        rol=usuario.rol
    )

    return{
        "access_token": token,
        "token_type": "bearer"
    }

@router.get(
    "/me",
    response_model=UsuarioActualResponse,
    responses={
        401: {"description": "No autenticado o token inválido"}
    }
)
def mi_perfil(
    usuario: Usuario = Depends(
        obtener_usuario_actual
    )
):
    return{
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol
    }
