from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.dependencies.roles import solo_paciente

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse

router = APIRouter()

RESPUESTAS_PACIENTE = {
    401: {"description": "No autenticado"},
    403: {"description": "Sin permisos: se requiere rol paciente"},
}

@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "El rol debe ser paciente"},
        409: {"description": "Correo o documento ya registrado"},
    }
)
def crear_paciente(
    datos: UsuarioCreate,
    db: Session = Depends(get_db)
):
    if datos.rol != "paciente":
        raise HTTPException(
            status_code=400,
            detail="El rol debe ser paciente"
        )
    
    usuario_email = db.query(Usuario).filter(
        Usuario.email == datos.email
    ).first()

    if usuario_email:
        raise HTTPException(
            status_code=409,
            detail="El correo electrónico ya está registrado"
        )
    
    usuario_documento = db.query(Usuario).filter(
        Usuario.documento == datos.documento
    ).first()

    if usuario_documento:
        raise HTTPException(
            status_code=409,
            detail="El documento ya está registrado"
        )
    
    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        documento=datos.documento,
        telefono=datos.telefono,
        email=datos.email,
        password=hash_password(datos.password),
        rol=datos.rol
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario

@router.get("/zona-paciente", responses=RESPUESTAS_PACIENTE)
def zona_paciente(
    usuario: Usuario = Depends(solo_paciente)
):
    return{
        "mensaje": "Acceso autorizado para paciente",
        "usuario": usuario.nombre,
        "rol": usuario.rol
    }
