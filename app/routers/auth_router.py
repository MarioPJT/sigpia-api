"""
auth_router.py - Endpoint de autenticación para SIGPIA
Gestiona el login y emisión de tokens JWT
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.usuario import Usuario
from app.core.security import verify_password, create_access_token


# ── Router ─────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


# ── Schema de entrada ──────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email    : EmailStr
    password : str


# ── Schema de respuesta ────────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token : str
    token_type   : str = "bearer"


# ── Endpoint ───────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Autentica un usuario con email y contraseña.
    Retorna un token JWT con duración de 30 minutos.
    """
    # 1. Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()

    # 2. Validar existencia y contraseña — mismo error para no revelar información
    if not usuario or not verify_password(data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verificar que la cuenta esté activa
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta se encuentra inactiva. Contacte al administrador.",
        )

    # 4. Generar token con payload de identidad y rol
    token = create_access_token(data={
        "sub"     : usuario.email,
        "rol"     : usuario.rol,
        "user_id" : usuario.id,
    })

    return TokenResponse(access_token=token)