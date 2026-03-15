"""
arbol_objetivo.py - Modelo SQLAlchemy para Árbol de Objetivos en SIGPIA
Tabla: arbol_objetivos
Transforma causas/efectos del árbol de problemas en medios/fines de solución.
"""

import enum
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


# ── Enum de tipos ──────────────────────────────────────────────────────────────
class TipoObjetivo(str, enum.Enum):
    MEDIO = "MEDIO"
    FIN   = "FIN"


# ── Modelo ─────────────────────────────────────────────────────────────────────
class ArbolObjetivo(Base):
    __tablename__ = "arbol_objetivos"

    id          = Column(Integer,           primary_key=True, autoincrement=True, index=True)
    descripcion = Column(Text,              nullable=True)
    tipo        = Column(Enum(TipoObjetivo), nullable=False)
    problema_id = Column(Integer,           ForeignKey("problemas.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    problema = relationship("Problema", back_populates="arbol_objetivos", lazy="select")

    def __repr__(self) -> str:
        return f"<ArbolObjetivo id={self.id} tipo={self.tipo} problema_id={self.problema_id}>"