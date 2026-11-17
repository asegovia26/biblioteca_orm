"""Modelo ORM para la entidad Socio."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.base import Base

if TYPE_CHECKING:
    from app.modelos.prestamo import Prestamo


class Socio(Base):
    """Representa a un socio lector de la biblioteca."""

    __tablename__ = "socios"

    id_socio: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dni: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fecha_alta: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    prestamos: Mapped[list[Prestamo]] = relationship(
        back_populates="socio",
        cascade="all, delete-orphan",
    )

    @property
    def nombre_completo(self) -> str:
        """Devuelve nombre y apellidos concatenados."""
        return f"{self.nombre} {self.apellidos}".strip()

    def __repr__(self) -> str:
        return (
            f"Socio(id_socio={self.id_socio!r}, dni={self.dni!r}, "
            f"nombre={self.nombre_completo!r}, activo={self.activo!r})"
        )
