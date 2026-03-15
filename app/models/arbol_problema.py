"""
arbol_problema.py - Modelo SQLAlchemy para Árbol de Problemas en SIGPIA
Tabla: arbol_problemas
Cada nodo representa una CAUSA o EFECTO asociado a un Problema.
"""

import enum
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


# ── Enum de tipos ──────────────────────────────────────────────────────────────
class TipoNodo(str, enum.Enum):
    CAUSA  = "CAUSA"
    EFECTO = "EFECTO"


# ── Modelo ─────────────────────────────────────────────────────────────────────
class ArbolProblema(Base):
    __tablename__ = "arbol_problemas"

    id          = Column(Integer,        primary_key=True, autoincrement=True, index=True)
    descripcion = Column(Text,           nullable=True)
    tipo        = Column(Enum(TipoNodo), nullable=False)
    problema_id = Column(Integer,        ForeignKey("problemas.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    problema = relationship("Problema", back_populates="arbol_nodos", lazy="select")

    def __repr__(self) -> str:
        return f"<ArbolProblema id={self.id} tipo={self.tipo} problema_id={self.problema_id}>"