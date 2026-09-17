from sqlalchemy import Column, Integer, String

from app.database import Base

class Usuario(Base):
    __tablename__="usuario"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    documento = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    telefono = Column(
        String(20),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    rol = Column(
        String(20),
        nullable=False
    )