from fastapi import Depends, HTTPException, status

from app.dependencies.auth import obtener_usuario_actual
from app.models.usuario import Usuario

def solo_paciente(
        usuario: Usuario = Depends(obtener_usuario_actual)
):
    if usuario.rol != "paciente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso permitido únicamente a paciente"
        )
    
    return usuario

def solo_medico(
        usuario: Usuario = Depends(obtener_usuario_actual)
):
    if usuario.rol != "medico":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso permitido únicamente a médico"
        )
    
    return usuario