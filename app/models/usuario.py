"""
usuario.py - Modelo de Usuario
Tabla: usuarios
"""

from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RolUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    CONSULTA = "CONSULTA"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    rol = Column(Enum(RolUsuario), nullable=False)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # 🔹 RELACIÓN CON PROYECTOS
    proyectos = relationship("Proyecto", back_populates="usuario")