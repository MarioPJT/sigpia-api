"""
problema_schema.py - Schemas Pydantic para Problema en SIGPIA
"""

from typing import Optional

from pydantic import BaseModel, Field


# ── Base ───────────────────────────────────────────────────────────────────────
class ProblemaBase(BaseModel):
    """Campos comunes compartidos entre schemas."""
    descripcion : Optional[str] = Field(None, example="Deficiencia en el suministro de agua potable.")
    impacto     : Optional[str] = Field(None, example="Afecta a 3.000 habitantes de la zona rural.")
    proyecto_id : int           = Field(...,  example=1)


# ── Create ─────────────────────────────────────────────────────────────────────
class ProblemaCreate(ProblemaBase):
    """Payload para registrar un nuevo problema asociado a un proyecto."""
    pass


# ── Update ─────────────────────────────────────────────────────────────────────
class ProblemaUpdate(BaseModel):
    """Payload para actualizar un problema. Todos los campos son opcionales."""
    descripcion : Optional[str] = Field(None)
    impacto     : Optional[str] = Field(None)
    proyecto_id : Optional[int] = Field(None)


# ── Response ───────────────────────────────────────────────────────────────────
class ProblemaResponse(ProblemaBase):
    """Payload de respuesta con todos los campos del problema."""
    id: int

    class Config:
        from_attributes = True