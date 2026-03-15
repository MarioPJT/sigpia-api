"""
usuario_schema.py - Schemas Pydantic para Usuario en SIGPIA
"""

from datetime import datetime
from typing import Optional
import enum

from pydantic import BaseModel, EmailStr, Field


# ── Enum de roles ──────────────────────────────────────────────────────────────
class RolUsuarioSchema(str, enum.Enum):
    ADMIN    = "ADMIN"
    CONSULTA = "CONSULTA"


# ── Base ───────────────────────────────────────────────────────────────────────
class UsuarioBase(BaseModel):
    """Campos comunes compartidos entre schemas."""
    nombre : str            = Field(..., max_length=100, example="María López")
    email  : EmailStr       = Field(...,                 example="maria@sigpia.gob")
    rol    : RolUsuarioSchema = Field(RolUsuarioSchema.CONSULTA, example="CONSULTA")
    activo : bool           = Field(True)


# ── Create ─────────────────────────────────────────────────────────────────────
class UsuarioCreate(UsuarioBase):
    """Payload para crear un nuevo usuario. Recibe contraseña en texto plano."""
    password: str = Field(..., min_length=8, example="S3cret!2024")


# ── Update ─────────────────────────────────────────────────────────────────────
class UsuarioUpdate(BaseModel):
    """Payload para actualizar un usuario. Todos los campos son opcionales."""
    nombre   : Optional[str]              = Field(None, max_length=100)
    email    : Optional[EmailStr]         = Field(None)
    rol      : Optional[RolUsuarioSchema] = Field(None)
    activo   : Optional[bool]             = Field(None)
    password : Optional[str]             = Field(None, min_length=8)


# ── Response ───────────────────────────────────────────────────────────────────
class UsuarioResponse(UsuarioBase):
    """Payload de respuesta. Nunca expone password_hash."""
    id             : int
    fecha_creacion : datetime

    class Config:
        from_attributes = True