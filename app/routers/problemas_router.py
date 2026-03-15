"""
problemas_router.py - CRUD completo de Problemas para SIGPIA
Cada problema está asociado a un proyecto existente.
ADMIN puede crear/editar/eliminar. CONSULTA solo puede ver.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.problema import Problema
from app.models.proyecto import Proyecto
from app.models.usuario import Usuario, RolUsuario
from app.schemas.problema_schema import ProblemaCreate, ProblemaUpdate, ProblemaResponse
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
            detail="No tienes permisos para realizar esta acción. Se requiere rol ADMIN.",
        )
    return current_user


# ── Helpers internos ───────────────────────────────────────────────────────────
def _get_problema_or_404(db: Session, problema_id: int) -> Problema:
    problema = db.query(Problema).filter(Problema.id == problema_id).first()
    if not problema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problema con id={problema_id} no encontrado.",
        )
    return problema


def _get_proyecto_or_404(db: Session, proyecto_id: int) -> Proyecto:
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyecto con id={proyecto_id} no encontrado.",
        )
    return proyecto


# ── Router ─────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/problemas",
    tags=["Problemas"],
)


# ── GET /problemas ─────────────────────────────────────────────────────────────
@router.get("/", response_model=list[ProblemaResponse])
def listar_problemas(
    skip: int = 0,
    limit: int = 100,
    proyecto_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),          # ADMIN y CONSULTA
):
    """
    Retorna todos los problemas. 
    Filtra por proyecto_id si se proporciona como query param.
    """
    query = db.query(Problema)
    if proyecto_id is not None:
        query = query.filter(Problema.proyecto_id == proyecto_id)
    return query.offset(skip).limit(limit).all()


# ── GET /problemas/{id} ────────────────────────────────────────────────────────
@router.get("/{problema_id}", response_model=ProblemaResponse)
def obtener_problema(
    problema_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),          # ADMIN y CONSULTA
):
    """Retorna un problema por su ID."""
    return _get_problema_or_404(db, problema_id)


# ── POST /problemas ────────────────────────────────────────────────────────────
@router.post("/", response_model=ProblemaResponse, status_code=status.HTTP_201_CREATED)
def crear_problema(
    payload: ProblemaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),             # solo ADMIN
):
    """
    Crea un nuevo problema asociado a un proyecto.
    Valida que el proyecto exista antes de insertar.
    """
    _get_proyecto_or_404(db, payload.proyecto_id)    # 404 si el proyecto no existe

    nuevo = Problema(
        descripcion = payload.descripcion,
        impacto     = payload.impacto,
        proyecto_id = payload.proyecto_id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ── PUT /problemas/{id} ────────────────────────────────────────────────────────
@router.put("/{problema_id}", response_model=ProblemaResponse)
def actualizar_problema(
    problema_id: int,
    payload: ProblemaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),             # solo ADMIN
):
    """
    Actualiza parcialmente un problema.
    Si se cambia proyecto_id, valida que el nuevo proyecto exista.
    """
    problema = _get_problema_or_404(db, problema_id)

    # Validar nuevo proyecto si se está reasignando
    if payload.proyecto_id is not None and payload.proyecto_id != problema.proyecto_id:
        _get_proyecto_or_404(db, payload.proyecto_id)

    for campo, valor in payload.dict(exclude_unset=True).items():
        setattr(problema, campo, valor)

    db.commit()
    db.refresh(problema)
    return problema


# ── DELETE /problemas/{id} ─────────────────────────────────────────────────────
@router.delete("/{problema_id}", status_code=status.HTTP_200_OK)
def eliminar_problema(
    problema_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),             # solo ADMIN
):
    """Elimina un problema por su ID."""
    problema = _get_problema_or_404(db, problema_id)
    db.delete(problema)
    db.commit()
    return {"detail": f"Problema id={problema_id} eliminado correctamente."}