from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.dependencies.roles import (
    solo_medico,
    solo_paciente
)
from app.models.cita import Cita
from app.models.disponibilidad import Disponibilidad
from app.models.medico_models import Medico
from app.models.usuario import Usuario
from app.schemas.citas_schema import (
    Citacreate,
    CitaResponse,
    EstadoCitaUpdate
)

router = APIRouter()


def obtener_medico_desde_usuario(
    usuario: Usuario,
    db: Session
):
    medico = db.query(Medico).filter(
        Medico.usuario_id == usuario.id
    ).first()

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de médico no encontrado"
        )

    return medico

@router.post(
    "/",
    response_model=CitaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {
            "description": "Médico no encontrado"
        },
        409: {
            "description": "Horario no disponible"
        }
    }
)
def crear_cita(
    datos: Citacreate,
    usuario: Usuario = Depends(solo_paciente),
    db: Session = Depends(get_db)
):
    medico = db.query(Medico).filter(
        Medico.id == datos.medico_id
    ).first()

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico no encontrado"
        )

    disponibilidad = db.query(
        Disponibilidad
    ).filter(
        Disponibilidad.medico_id == datos.medico_id,
        Disponibilidad.fecha == datos.fecha,
        Disponibilidad.hora_inicio <= datos.hora,
        Disponibilidad.hora_fin > datos.hora
    ).first()

    if disponibilidad is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Horario no disponible"
        )

    cita_existente = db.query(Cita).filter(
        Cita.medico_id == datos.medico_id,
        Cita.fecha == datos.fecha,
        Cita.hora == datos.hora,
        Cita.estado != "cancelada"
    ).first()

    if cita_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Horario no disponible"
        )

    nueva_cita = Cita(
        paciente_id=usuario.id,
        medico_id=datos.medico_id,
        fecha=datos.fecha,
        hora=datos.hora,
        motivo=datos.motivo,
        estado="pendiente"
    )

    db.add(nueva_cita)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Horario no disponible"
        )
    db.refresh(nueva_cita)

    return nueva_cita

@router.get(
    "/mis-citas",
    response_model=list[CitaResponse]
)
def consultar_mis_citas(
    usuario: Usuario = Depends(solo_paciente),
    db: Session = Depends(get_db)
):
    citas = db.query(Cita).filter(
        Cita.paciente_id == usuario.id
    ).order_by(
        Cita.fecha,
        Cita.hora
    ).all()

    return citas

@router.get(
    "/agenda",
    response_model=list[CitaResponse]
)
def consultar_agenda(
    usuario: Usuario = Depends(solo_medico),
    db: Session = Depends(get_db)
):
    medico = obtener_medico_desde_usuario(
        usuario,
        db
    )

    citas = db.query(Cita).filter(
        Cita.medico_id == medico.id
    ).order_by(
        Cita.fecha,
        Cita.hora
    ).all()

    return citas

@router.patch(
    "/{cita_id}/estado",
    response_model=CitaResponse,
    responses={
        404: {
            "description": "Cita no encontrada"
        }
    }
)
def actualizar_estado_cita(
    cita_id: int,
    datos: EstadoCitaUpdate,
    usuario: Usuario = Depends(solo_medico),
    db: Session = Depends(get_db)
):
    medico = obtener_medico_desde_usuario(
        usuario,
        db
    )

    cita = db.query(Cita).filter(
        Cita.id == cita_id,
        Cita.medico_id == medico.id
    ).first()

    if cita is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )

    if cita.estado == "cancelada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La cita ya está cancelada"
        )

    cita.estado = datos.estado

    db.commit()
    db.refresh(cita)

    return cita

@router.delete(
    "/{cita_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "description": "Cita no encontrada"
        },
        409: {
            "description": "La cita ya está cancelada"
        }
    }
)
def cancelar_cita(
    cita_id: int,
    usuario: Usuario = Depends(solo_paciente),
    db: Session = Depends(get_db)
):
    cita = db.query(Cita).filter(
        Cita.id == cita_id,
        Cita.paciente_id == usuario.id
    ).first()

    if cita is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )

    if cita.estado == "cancelada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La cita ya está cancelada"
        )

    cita.estado = "cancelada"

    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
