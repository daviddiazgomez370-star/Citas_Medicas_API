from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import obtener_usuario_actual
from app.dependencies.roles import solo_medico
from app.models.cita import Cita
from app.models.disponibilidad import Disponibilidad
from app.models.medico_models import Medico
from app.models.usuario import Usuario
from app.schemas.disponibilidad_schema import (
    DisponibilidadCreate,
    DisponibilidadResponse,
    DisponibilidadUpdate
)

router = APIRouter()

RESPUESTAS_MEDICO = {
    401: {"description": "No autenticado"},
    403: {"description": "Sin permisos: se requiere rol médico"},
}

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

def existe_cruce_horario(
    db: Session,
    medico_id: int,
    fecha,
    hora_inicio,
    hora_fin,
    excluir_id: int | None = None
):
    consulta = db.query(Disponibilidad).filter(
        Disponibilidad.medico_id == medico_id,
        Disponibilidad.fecha == fecha,
        Disponibilidad.hora_inicio < hora_fin,
        Disponibilidad.hora_fin > hora_inicio
    )

    if excluir_id is not None:
        consulta = consulta.filter(
            Disponibilidad.id != excluir_id
        )

    return consulta.first()


def existen_citas_afectadas(
    db: Session,
    disponibilidad: Disponibilidad,
    nueva_fecha=None,
    nueva_hora_inicio=None,
    nueva_hora_fin=None
) -> bool:
    """Evita retirar de la disponibilidad citas activas ya agendadas."""
    citas = db.query(Cita).filter(
        Cita.medico_id == disponibilidad.medico_id,
        Cita.fecha == disponibilidad.fecha,
        Cita.hora >= disponibilidad.hora_inicio,
        Cita.hora < disponibilidad.hora_fin,
        Cita.estado != "cancelada"
    ).all()

    if nueva_fecha is None:
        return bool(citas)

    return any(
        cita.fecha != nueva_fecha
        or cita.hora < nueva_hora_inicio
        or cita.hora >= nueva_hora_fin
        for cita in citas
    )

@router.post(
    "/",
    response_model=DisponibilidadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        **RESPUESTAS_MEDICO,
        404: {"description": "Perfil de médico no encontrado"},
        409: {"description": "Horario superpuesto o conflicto de reserva"},
    }
)
def crear_disponibilidad(
    datos: DisponibilidadCreate,
    usuario: Usuario = Depends(solo_medico),
    db: Session = Depends(get_db)
):
    medico = obtener_medico_desde_usuario(
        usuario,
        db
    )

    horario_existente = existe_cruce_horario(
        db=db,
        medico_id=medico.id,
        fecha=datos.fecha,
        hora_inicio=datos.hora_inicio,
        hora_fin=datos.hora_fin
    )

    if horario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El horario se cruza con otra "
                "disponibilidad existente"
            )
        )

    nueva_disponibilidad = Disponibilidad(
        medico_id=medico.id,
        fecha=datos.fecha,
        hora_inicio=datos.hora_inicio,
        hora_fin=datos.hora_fin
    )

    db.add(nueva_disponibilidad)
    db.commit()
    db.refresh(nueva_disponibilidad)

    return nueva_disponibilidad

@router.get(
    "/mia",
    response_model=list[DisponibilidadResponse],
    responses={
        **RESPUESTAS_MEDICO,
        404: {"description": "Perfil de médico no encontrado"},
    }
)
def consultar_mi_disponibilidad(
    usuario: Usuario = Depends(solo_medico),
    db: Session = Depends(get_db)
):
    medico = obtener_medico_desde_usuario(
        usuario,
        db
    )

    disponibilidades = db.query(
        Disponibilidad
    ).filter(
        Disponibilidad.medico_id == medico.id
    ).order_by(
        Disponibilidad.fecha,
        Disponibilidad.hora_inicio
    ).all()

    return disponibilidades

@router.get(
    "/medico/{medico_id}",
    response_model=list[DisponibilidadResponse],
    responses={
        401: {"description": "No autenticado"},
        404: {"description": "Médico no encontrado"},
    }
)
def consultar_disponibilidad_medico(
    medico_id: int,
    usuario: Usuario = Depends(
        obtener_usuario_actual
    ),
    db: Session = Depends(get_db)
):
    medico = db.query(Medico).filter(
        Medico.id == medico_id
    ).first()

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico no encontrado"
        )

    disponibilidades = db.query(
        Disponibilidad
    ).filter(
        Disponibilidad.medico_id == medico_id
    ).order_by(
        Disponibilidad.fecha,
        Disponibilidad.hora_inicio
    ).all()

    return disponibilidades

@router.put(
    "/{disponibilidad_id}",
    response_model=DisponibilidadResponse,
    responses={
        **RESPUESTAS_MEDICO,
        404: {"description": "Disponibilidad no encontrada"},
        409: {"description": "Horario superpuesto o citas activas afectadas"},
    }
)
def actualizar_disponibilidad(
    disponibilidad_id: int,
    datos: DisponibilidadUpdate,
    usuario: Usuario = Depends(solo_medico),
    db: Session = Depends(get_db)
):
    medico = obtener_medico_desde_usuario(
        usuario,
        db
    )

    disponibilidad = db.query(
        Disponibilidad
    ).filter(
        Disponibilidad.id == disponibilidad_id,
        Disponibilidad.medico_id == medico.id
    ).first()

    if disponibilidad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disponibilidad no encontrada"
        )

    horario_existente = existe_cruce_horario(
        db=db,
        medico_id=medico.id,
        fecha=datos.fecha,
        hora_inicio=datos.hora_inicio,
        hora_fin=datos.hora_fin,
        excluir_id=disponibilidad.id
    )

    if horario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El horario se cruza con otra "
                "disponibilidad existente"
            )
        )

    if existen_citas_afectadas(
        db,
        disponibilidad,
        datos.fecha,
        datos.hora_inicio,
        datos.hora_fin
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede modificar una disponibilidad con citas activas afectadas"
        )

    disponibilidad.fecha = datos.fecha
    disponibilidad.hora_inicio = datos.hora_inicio
    disponibilidad.hora_fin = datos.hora_fin

    db.commit()
    db.refresh(disponibilidad)

    return disponibilidad

@router.delete(
    "/{disponibilidad_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **RESPUESTAS_MEDICO,
        404: {"description": "Disponibilidad no encontrada"},
        409: {"description": "La disponibilidad tiene citas activas"},
    }
)
def eliminar_disponibilidad(
    disponibilidad_id: int,
    usuario: Usuario = Depends(solo_medico),
    db: Session = Depends(get_db)
):
    medico = obtener_medico_desde_usuario(
        usuario,
        db
    )

    disponibilidad = db.query(
        Disponibilidad
    ).filter(
        Disponibilidad.id == disponibilidad_id,
        Disponibilidad.medico_id == medico.id
    ).first()

    if disponibilidad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disponibilidad no encontrada"
        )

    if existen_citas_afectadas(db, disponibilidad):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar una disponibilidad con citas activas"
        )

    db.delete(disponibilidad)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
