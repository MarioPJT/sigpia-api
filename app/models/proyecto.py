"""
proyecto.py - Modelo de Proyecto para SIGPIA
Tabla: proyectos
"""

import enum
from sqlalchemy import (
    Column, Integer, String, Text,
    TIMESTAMP, Enum, ForeignKey, text
)
from sqlalchemy.orm import relationship

from app.database import Base


# ── Enum de estados ────────────────────────────────────────────────────────────
class EstadoProyecto(str, enum.Enum):
    BORRADOR       = "BORRADOR"
    EN_EVALUACION  = "EN_EVALUACION"
    APROBADO       = "APROBADO"
    RECHAZADO      = "RECHAZADO"


# ── Modelo ─────────────────────────────────────────────────────────────────────
class Proyecto(Base):
    __tablename__ = "proyectos"

    # Columnas
    id             = Column(Integer,            primary_key=True, autoincrement=True, index=True)
    nombre         = Column(String(200),        nullable=False)
    sector         = Column(String(100),        nullable=True)
    descripcion    = Column(Text,               nullable=True)
    estado         = Column(Enum(EstadoProyecto, name="estado_proyecto_enum"), nullable=False, default=EstadoProyecto.BORRADOR)
    fecha_creacion = Column(TIMESTAMP,          nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    usuario_id     = Column(Integer,            ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="proyectos", lazy="select")
    problema = relationship("Problema", back_populates="proyecto", uselist=False, cascade="all, delete-orphan")

    # Representación
    def __repr__(self) -> str:
        return f"<Proyecto id={self.id} nombre={self.nombre!r} estado={self.estado}>"