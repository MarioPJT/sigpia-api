"""
arbol_problema_schema.py - Schemas Pydantic para Árbol de Problemas en SIGPIA
"""

import enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enum de tipos ──────────────────────────────────────────────────────────────
class TipoNodoSchema(str, enum.Enum):
    CAUSA  = "CAUSA"
    EFECTO = "EFECTO"


# ── Base ───────────────────────────────────────────────────────────────────────
class ArbolProblemaBase(BaseModel):
    descripcion : Optional[str]   = Field(None, example="Falta de infraestructura hídrica.")
    tipo        : TipoNodoSchema  = Field(...,  example="CAUSA")
    problema_id : int             = Field(...,  example=1)


# ── Create ─────────────────────────────────────────────────────────────────────
class ArbolProblemaCreate(ArbolProblemaBase):
    """Payload para registrar un nodo (causa o efecto) en el árbol de un problema."""
    pass


# ── Update ─────────────────────────────────────────────────────────────────────
class ArbolProblemaUpdate(BaseModel):
    """Actualización parcial. Todos los campos son opcionales."""
    descripcion : Optional[str]        = Field(None)
    tipo        : Optional[TipoNodoSchema] = Field(None)
    problema_id : Optional[int]        = Field(None, example=2)


# ── Response ───────────────────────────────────────────────────────────────────
class ArbolProblemaResponse(ArbolProblemaBase):
    """Payload de respuesta con todos los campos del nodo."""
    id: int

    class Config:
        from_attributes = True