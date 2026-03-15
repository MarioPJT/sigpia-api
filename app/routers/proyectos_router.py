"""
proyectos_router.py - CRUD completo de Proyectos para SIGPIA
Protegido con JWT. ADMIN puede crear/editar/eliminar. CONSULTA solo puede ver.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.proyecto import Proyecto
from app.models.usuario import Usuario
from app.schemas.proyecto_schema import ProyectoCreate, ProyectoUpdate, ProyectoResponse
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
    if current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol ADMIN.",
        )
    return current_user


# ── Helpers internos ───────────────────────────────────────────────────────────
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
    prefix="/proyectos",
    tags=["Proyectos"],
)


# ── GET /proyectos ─────────────────────────────────────────────────────────────
@router.get("/", response_model=list[ProyectoResponse])
def listar_proyectos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),        # ADMIN y CONSULTA
):
    """Retorna todos los proyectos registrados. Paginación con skip/limit."""
    return db.query(Proyecto).offset(skip).limit(limit).all()


# ── GET /proyectos/{id} ────────────────────────────────────────────────────────
@router.get("/{proyecto_id}", response_model=ProyectoResponse)
def obtener_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),        # ADMIN y CONSULTA
):
    """Retorna un proyecto por su ID."""
    return _get_proyecto_or_404(db, proyecto_id)


# ── POST /proyectos ────────────────────────────────────────────────────────────
@router.post("/", response_model=ProyectoResponse, status_code=status.HTTP_201_CREATED)
def crear_proyecto(
    payload: ProyectoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),  # solo ADMIN
):
    """Crea un nuevo proyecto. Si no se especifica usuario_id, se asigna al usuario autenticado."""
    nuevo = Proyecto(
        nombre      = payload.nombre,
        sector      = payload.sector,
        descripcion = payload.descripcion,
        estado      = payload.estado,
        usuario_id  = payload.usuario_id or current_user.id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ── PUT /proyectos/{id} ────────────────────────────────────────────────────────
@router.put("/{proyecto_id}", response_model=ProyectoResponse)
def actualizar_proyecto(
    proyecto_id: int,
    payload: ProyectoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),             # solo ADMIN
):
    """Actualiza parcialmente un proyecto existente."""
    proyecto = _get_proyecto_or_404(db, proyecto_id)

    for campo, valor in payload.dict(exclude_unset=True).items():
        setattr(proyecto, campo, valor)

    db.commit()
    db.refresh(proyecto)
    return proyecto


# ── DELETE /proyectos/{id} ─────────────────────────────────────────────────────
@router.delete("/{proyecto_id}", status_code=status.HTTP_200_OK)
def eliminar_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),             # solo ADMIN
):
    """Elimina un proyecto y sus registros dependientes (CASCADE en BD)."""
    proyecto = _get_proyecto_or_404(db, proyecto_id)
    db.delete(proyecto)
    db.commit()
    return {"detail": f"Proyecto id={proyecto_id} eliminado correctamente."}