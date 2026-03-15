"""
problema.py - Modelo de Problema para SIGPIA
Tabla: problemas
"""

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Problema(Base):
    __tablename__ = "problemas"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    descripcion = Column(Text, nullable=True)
    impacto = Column(Text, nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))

    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"), nullable=False, unique=True)
    arbol_nodos = relationship("ArbolProblema", back_populates="problema")

    proyecto = relationship( "Proyecto", back_populates="problema", uselist=False)

    def __repr__(self):
        return f"<Problema id={self.id} proyecto_id={self.proyecto_id}>"