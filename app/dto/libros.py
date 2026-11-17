"""DTOs para la gestión del catálogo de libros."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DatosLibro:
    """Datos de entrada para crear un nuevo libro."""

    isbn: str
    titulo: str
    precio: Decimal
    id_autor: int


@dataclass(frozen=True)
class LibroResumen:
    """DTO de salida con información resumida de un libro."""

    id_libro: int
    titulo: str
    autor: str
    precio: Decimal


@dataclass(frozen=True)
class FiltroLibros:
    """Criterios dinámicos de filtrado y paginación para libros."""

    texto: str | None = None
    precio_minimo: Decimal | None = None
    precio_maximo: Decimal | None = None
    id_autor: int | None = None
    solo_activos: bool = True
    pagina: int = 1
    tamano: int = 10
