"""
arbol_objetivo_router.py - CRUD de Árbol de Objetivos para SIGPIA
Cada nodo representa un MEDIO o FIN derivado del árbol de problemas.
ADMIN puede crear/editar/eliminar. CONSULTA solo puede ver.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.arbol_objetivo import ArbolObjetivo
from app.models.problema import Problema
from app.models.usuario import Usuario, RolUsuario
from app.schemas.arbol_objetivo_schema import (
    ArbolObjetivoCreate,
    ArbolObjetivoUpdate,
    ArbolObjetivoResponse,
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
def _get_nodo_or_404(db: Session, nodo_id: int) -> ArbolObjetivo:
    nodo = db.query(ArbolObjetivo).filter(ArbolObjetivo.id == nodo_id).first()
    if not nodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nodo de árbol de objetivos con id={nodo_id} no encontrado.",
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
    prefix="/arbol-objetivos",
    tags=["Árbol de Objetivos"],
)


# ── GET /arbol-objetivos ───────────────────────────────────────────────────────
@router.get("/", response_model=list[ArbolObjetivoResponse])
def listar_nodos(
    skip: int = 0,
    limit: int = 100,
    problema_id: int | None = None,
    tipo: str | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),            # ADMIN y CONSULTA
):
    """
    Retorna todos los nodos del árbol de objetivos.
    Filtros opcionales: ?problema_id=N  |  ?tipo=MEDIO  |  ?tipo=FIN
    """
    query = db.query(ArbolObjetivo)

    if problema_id is not None:
        query = query.filter(ArbolObjetivo.problema_id == problema_id)
    if tipo is not None:
        query = query.filter(ArbolObjetivo.tipo == tipo.upper())

    return query.offset(skip).limit(limit).all()


# ── GET /arbol-objetivos/{id} ──────────────────────────────────────────────────
@router.get("/{nodo_id}", response_model=ArbolObjetivoResponse)
def obtener_nodo(
    nodo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),            # ADMIN y CONSULTA
):
    """Retorna un nodo del árbol de objetivos por su ID."""
    return _get_nodo_or_404(db, nodo_id)


# ── POST /arbol-objetivos ──────────────────────────────────────────────────────
@router.post("/", response_model=ArbolObjetivoResponse, status_code=status.HTTP_201_CREATED)
def crear_nodo(
    payload: ArbolObjetivoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),               # solo ADMIN
):
    """
    Crea un nodo (MEDIO o FIN) en el árbol de objetivos.
    Valida que el problema asociado exista antes de insertar.
    """
    _get_problema_or_404(db, payload.problema_id)

    nuevo = ArbolObjetivo(
        descripcion = payload.descripcion,
        tipo        = payload.tipo,
        problema_id = payload.problema_id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ── PUT /arbol-objetivos/{id} ──────────────────────────────────────────────────
@router.put("/{nodo_id}", response_model=ArbolObjetivoResponse)
def actualizar_nodo(
    nodo_id: int,
    payload: ArbolObjetivoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),               # solo ADMIN
):
    """
    Actualiza parcialmente un nodo del árbol de objetivos.
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


# ── DELETE /arbol-objetivos/{id} ───────────────────────────────────────────────
@router.delete("/{nodo_id}", status_code=status.HTTP_200_OK)
def eliminar_nodo(
    nodo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),               # solo ADMIN
):
    """Elimina un nodo del árbol de objetivos por su ID."""
    nodo = _get_nodo_or_404(db, nodo_id)
    db.delete(nodo)
    db.commit()
    return {"detail": f"Nodo id={nodo_id} eliminado correctamente."}