from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.dependencies.roles import solo_medico

from app.database import get_db
from app.models.medico_models import Medico
from app.models.usuario import Usuario
from app.schemas.medico_schema import MedicoCreate

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_medico(datos: MedicoCreate, db: Session = Depends(get_db)):
    usuario_email = db.query(Usuario).filter(Usuario.email == datos.email).first()

    if usuario_email:
        raise HTTPException(
            status_code=409, detail="El correo electrónico ya está registrado"
        )

    usuario_documento = (
        db.query(Usuario).filter(Usuario.documento == datos.documento).first()
    )

    if usuario_documento:
        raise HTTPException(status_code=409, detail="El documento ya está registrado")

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        documento=datos.documento,
        telefono=datos.telefono,
        email=datos.email,
        password=hash_password(datos.password),
        rol="medico",
    )

    db.add(nuevo_usuario)
    db.flush()

    nuevo_medico = Medico(usuario_id=nuevo_usuario.id, especialidad=datos.especialidad)

    db.add(nuevo_medico)

    db.commit()

    db.refresh(nuevo_usuario)
    db.refresh(nuevo_medico)

    return {
        "id": nuevo_medico.id,
        "usuario_id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "documento": nuevo_usuario.documento,
        "telefono": nuevo_usuario.telefono,
        "email": nuevo_usuario.email,
        "rol": nuevo_usuario.rol,
        "especialidad": nuevo_medico.especialidad,
    }


@router.get("/")
def listar_medicos(db: Session = Depends(get_db)):
    medicos = (
        db.query(Medico, Usuario).join(Usuario, Medico.usuario_id == Usuario.id).all()
    )

    resultado = []

    for medico, usuario in medicos:
        resultado.append(
            {
                "id": medico.id,
                "usuario_id": usuario.id,
                "nombre": usuario.nombre,
                "documento": usuario.documento,
                "telefono": usuario.telefono,
                "email": usuario.email,
                "especialidad": medico.especialidad,
            }
        )

    return resultado


@router.get("/zona-medico")
def zona_medico(usuario: Usuario = Depends(solo_medico)):
    return {
        "mensaje": "Acceso autorizado para médico",
        "usuario": usuario.nombre,
        "rol": usuario.rol,
    }
