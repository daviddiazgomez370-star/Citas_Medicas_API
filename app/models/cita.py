from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String, Time, text

from app.database import Base

class Cita(Base):
    __tablename__= "citas"

    __table_args__ = (
        Index(
            "uq_citas_medico_fecha_hora_activa",
            "medico_id",
            "fecha",
            "hora",
            unique=True,
            sqlite_where=text("estado != 'cancelada'")
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    paciente_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
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

    hora = Column(
        Time, 
        nullable=False
    )

    motivo = Column(
        String(255),
        nullable=False
    )

    estado = Column(
        String(20),
        nullable=False,
        default="pendiente"
    )
