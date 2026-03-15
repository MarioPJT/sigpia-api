"""
security.py - Utilidades de seguridad para SIGPIA
Hash de contraseñas con bcrypt y generación/validación de JWT
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

import os
from dotenv import load_dotenv

# ── Configuración ──────────────────────────────────────────────────────────────
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM             = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ── Contexto de hashing ────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Contraseñas ────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Genera el hash bcrypt de una contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña en texto plano coincida con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT ────────────────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JWT firmado con los datos proporcionados.

    Args:
        data:          Payload a incluir en el token (ej. {"sub": email, "rol": "ADMIN"}).
        expires_delta: Tiempo de vida personalizado. Por defecto, 30 minutos.

    Returns:
        Token JWT como string.
    """
    payload    = data.copy()
    expires_at = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expires_at})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT.

    Args:
        token: Token JWT como string.

    Returns:
        Payload decodificado como dict, o None si el token es inválido o expiró.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None