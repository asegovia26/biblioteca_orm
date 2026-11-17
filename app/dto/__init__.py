"""Objetos de transferencia de datos (DTO)."""

from app.dto.libros import DatosLibro, FiltroLibros, LibroResumen
from app.dto.prestamos import DatosPrestamo, PrestamoResumen

__all__ = [
    "DatosLibro",
    "LibroResumen",
    "FiltroLibros",
    "DatosPrestamo",
    "PrestamoResumen",
]
