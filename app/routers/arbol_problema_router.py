"""
arbol_problema_router.py - CRUD de Árbol de Problemas para SIGPIA
Cada nodo representa una CAUSA o EFECTO vinculado a un Problema existente.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.arbol_problema import ArbolProblema
from app.models.problema import Problema
from app.models.usuario import Usuario, RolUsuario
from app.schemas.arbol_problema_schema import (
    ArbolProblemaCreate,
    ArbolProblemaUpdate,
    ArbolProblemaResponse,
)
from app.core.security import decode_access_token


# ── Seguridad ──────────────────────────────────────────────────────────────────
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida el token JWT y retorna el usuario autenticado."""
    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = db.query(Usuario).filter(Usuario.email == payload.get("sub")).first()

    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
        )
    return usuario


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Restringe el acceso a usuarios con rol ADMIN."""
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción. Se requiere rol ADMIN.",
        )
    return current_user


# ── Helpers internos ───────────────────────────────────────────────────────────
def _get_nodo_or_404(db: Session, nodo_id: int) -> ArbolProblema:
    nodo = db.query(ArbolProblema).filter(ArbolProblema.id == nodo_id).first()
    if not nodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nodo de árbol con id={nodo_id} no encontrado.",
        )
    return nodo


def _get_problema_or_404(db: Session, problema_id: int) -> Problema:
    problema = db.query(Problema).filter(Problema.id == problema_id).first()
    if not problema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problema con id={problema_id} no encontrado.",
        )
    return problema


# ── Router ─────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/arbol-problemas",
    tags=["Árbol de Problemas"],
)


# ── GET /arbol-problemas ───────────────────────────────────────────────────────
@router.get("/", response_model=list[ArbolProblemaResponse])
def listar_nodos(
    skip: int = 0,
    limit: int = 100,
    problema_id: int | None = None,
    tipo: str | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),           # ADMIN y CONSULTA
):
    """
    Retorna todos los nodos del árbol de problemas.
    Filtros opcionales: ?problema_id=N  |  ?tipo=CAUSA  |  ?tipo=EFECTO
    """
    query = db.query(ArbolProblema)

    if problema_id is not None:
        query = query.filter(ArbolProblema.problema_id == problema_id)
    if tipo is not None:
        query = query.filter(ArbolProblema.tipo == tipo.upper())

    return query.offset(skip).limit(limit).all()


# ── GET /arbol-problemas/{id} ──────────────────────────────────────────────────
@router.get("/{nodo_id}", response_model=ArbolProblemaResponse)
def obtener_nodo(
    nodo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),           # ADMIN y CONSULTA
):
    """Retorna un nodo del árbol por su ID."""
    return _get_nodo_or_404(db, nodo_id)


# ── POST /arbol-problemas ──────────────────────────────────────────────────────
@router.post("/", response_model=ArbolProblemaResponse, status_code=status.HTTP_201_CREATED)
def crear_nodo(
    payload: ArbolProblemaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),              # solo ADMIN
):
    """
    Crea un nodo (CAUSA o EFECTO) en el árbol de un problema.
    Valida que el problema exista antes de insertar.
    """
    _get_problema_or_404(db, payload.problema_id)

    nuevo = ArbolProblema(
        descripcion = payload.descripcion,
        tipo        = payload.tipo,
        problema_id = payload.problema_id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ── PUT /arbol-problemas/{id} ──────────────────────────────────────────────────
@router.put("/{nodo_id}", response_model=ArbolProblemaResponse)
def actualizar_nodo(
    nodo_id: int,
    payload: ArbolProblemaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),              # solo ADMIN
):
    """
    Actualiza parcialmente un nodo del árbol.
    Si se cambia problema_id, valida que el nuevo problema exista.
    """
    nodo = _get_nodo_or_404(db, nodo_id)

    if payload.problema_id is not None and payload.problema_id != nodo.problema_id:
        _get_problema_or_404(db, payload.problema_id)

    for campo, valor in payload.dict(exclude_unset=True).items():
        setattr(nodo, campo, valor)

    db.commit()
    db.refresh(nodo)
    return nodo


# ── DELETE /arbol-problemas/{id} ───────────────────────────────────────────────
@router.delete("/{nodo_id}", status_code=status.HTTP_200_OK)
def eliminar_nodo(
    nodo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),              # solo ADMIN
):
    """Elimina un nodo del árbol de problemas por su ID."""
    nodo = _get_nodo_or_404(db, nodo_id)
    db.delete(nodo)
    db.commit()
    return {"detail": f"Nodo id={nodo_id} eliminado correctamente."}