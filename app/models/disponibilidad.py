from sqlalchemy import Column, Date, ForeignKey, Integer, Time

from app.database import Base

class Disponibilidad(Base):
    __tablename__= "disponibilidad"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    medico_id = Column(
        Integer,
        ForeignKey("medicos.id"),
        nullable=False,
        index=True
    )

    fecha = Column(
        Date,
        nullable=False
    )

    hora_inicio = Column(
        Time,
        nullable=False
    )

    hora_fin = Column(
        Time,
        nullable=False
    )

    