"""
arbol_objetivo_schema.py - Schemas Pydantic para Árbol de Objetivos en SIGPIA
"""

import enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enum de tipos ──────────────────────────────────────────────────────────────
class TipoObjetivoSchema(str, enum.Enum):
    MEDIO = "MEDIO"
    FIN   = "FIN"


# ── Base ───────────────────────────────────────────────────────────────────────
class ArbolObjetivoBase(BaseModel):
    descripcion : Optional[str]      = Field(None, example="Ampliar la cobertura de red hídrica.")
    tipo        : TipoObjetivoSchema = Field(...,  example="MEDIO")
    problema_id : int                = Field(...,  example=1)


# ── Create ─────────────────────────────────────────────────────────────────────
class ArbolObjetivoCreate(ArbolObjetivoBase):
    """Payload para registrar un nodo (medio o fin) en el árbol de objetivos."""
    pass


# ── Update ─────────────────────────────────────────────────────────────────────
class ArbolObjetivoUpdate(BaseModel):
    """Actualización parcial. Todos los campos son opcionales."""
    descripcion : Optional[str]             = Field(None)
    tipo        : Optional[TipoObjetivoSchema] = Field(None)
    problema_id : Optional[int]             = Field(None, example=2)


# ── Response ───────────────────────────────────────────────────────────────────
class ArbolObjetivoResponse(ArbolObjetivoBase):
    """Payload de respuesta con todos los campos del nodo."""
    id: int

    class Config:
        from_attributes = True