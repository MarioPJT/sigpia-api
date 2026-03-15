"""
proyecto_schema.py - Schemas Pydantic para Proyecto en SIGPIA
"""

from datetime import datetime
from typing import Optional
import enum

from pydantic import BaseModel, Field


# ── Enum de estados ────────────────────────────────────────────────────────────
class EstadoProyectoSchema(str, enum.Enum):
    BORRADOR      = "BORRADOR"
    EN_EVALUACION = "EN_EVALUACION"
    APROBADO      = "APROBADO"
    RECHAZADO     = "RECHAZADO"


# ── Base ───────────────────────────────────────────────────────────────────────
class ProyectoBase(BaseModel):
    """Campos comunes compartidos entre schemas."""
    nombre      : str                      = Field(...,  max_length=200, example="Construcción de acueducto rural")
    sector      : Optional[str]            = Field(None, max_length=100, example="Agua y Saneamiento")
    descripcion : Optional[str]            = Field(None, example="Proyecto de ampliación de red hídrica en zona rural.")
    estado      : EstadoProyectoSchema     = Field(EstadoProyectoSchema.BORRADOR, example="BORRADOR")
    usuario_id  : Optional[int]            = Field(None, example=1)


# ── Create ─────────────────────────────────────────────────────────────────────
class ProyectoCreate(ProyectoBase):
    """Payload para registrar un nuevo proyecto."""
    pass


# ── Update ─────────────────────────────────────────────────────────────────────
class ProyectoUpdate(BaseModel):
    """Payload para actualizar un proyecto. Todos los campos son opcionales."""
    nombre      : Optional[str]                  = Field(None, max_length=200)
    sector      : Optional[str]                  = Field(None, max_length=100)
    descripcion : Optional[str]                  = Field(None)
    estado      : Optional[EstadoProyectoSchema] = Field(None)
    usuario_id  : Optional[int]                  = Field(None)


# ── Response ───────────────────────────────────────────────────────────────────
class ProyectoResponse(ProyectoBase):
    """Payload de respuesta con todos los campos del proyecto."""
    id             : int
    fecha_creacion : datetime

    model_config = {
        "from_attributes": True
    }