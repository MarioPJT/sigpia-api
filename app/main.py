"""
main.py - Punto de entrada de SIGPIA
Sistema de Gestión de Inversión Pública con IA
"""

from fastapi import FastAPI
from app.models import arbol_objetivo
from app.routers import auth_router, proyectos_router
# from app.routers import usuarios_router      # descomentar cuando esté listo
from app.routers import problemas_router     # descomentar cuando esté listo
from app.routers import auth_router, proyectos_router, problemas_router, arbol_problema_router
from app.routers import arbol_objetivo_router


# ── Instancia ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "SIGPIA - Sistema de Gestión de Inversión Pública con IA",
    version     = "1.0.0",
    description = "API REST para gestión, evaluación y seguimiento de proyectos de inversión pública.",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── Routers ────────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth_router.router,      prefix=API_PREFIX)
app.include_router(proyectos_router.router, prefix=API_PREFIX)
# app.include_router(usuarios_router.router,  prefix=API_PREFIX)
app.include_router(problemas_router.router, prefix=API_PREFIX)
app.include_router(arbol_problema_router.router, prefix=API_PREFIX)
app.include_router(arbol_objetivo_router.router, prefix=API_PREFIX)

# ── Raíz ───────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Estado"])
def root() -> dict:
    return {
        "sistema" : "SIGPIA",
        "version" : "1.0.0",
        "estado"  : "operativo",
        "docs"    : "/docs",
    }