"""DTOs para la gestión de préstamos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DatosPrestamo:
    """Datos de entrada para registrar un préstamo."""

    id_socio: int
    id_ejemplar: int
    dias_plazo: int = 14
    observaciones: str | None = None


@dataclass(frozen=True)
class PrestamoResumen:
    """DTO de salida con el resumen de un préstamo."""

    id_prestamo: int
    socio: str
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: date | None
    ejemplares: list[str]
