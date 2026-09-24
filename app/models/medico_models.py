from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base

class Medico(Base):
    __tablename__= "medicos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        unique=True,
        nullable=False        
    )

    especialidad = Column(
        String(200),
        nullable=False
    )
