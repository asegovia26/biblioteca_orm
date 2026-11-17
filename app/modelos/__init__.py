"""Exportación centralizada de los modelos ORM."""

from app.modelos.autor import Autor
from app.modelos.base import Base
from app.modelos.ejemplar import Ejemplar
from app.modelos.libro import Libro
from app.modelos.prestamo import Prestamo, detalle_prestamo
from app.modelos.socio import Socio

__all__ = [
    "Base",
    "Autor",
    "Libro",
    "Ejemplar",
    "Socio",
    "Prestamo",
    "detalle_prestamo",
]
