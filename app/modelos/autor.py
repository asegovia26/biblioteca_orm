"""Modelo ORM para la entidad Autor."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.base import Base

if TYPE_CHECKING:
    from app.modelos.libro import Libro


class Autor(Base):
    """Representa a un autor de libros en el catálogo."""

    __tablename__ = "autores"
    __table_args__ = (UniqueConstraint("nombre", "apellidos", name="uq_autor"),)

    id_autor: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)
    nacionalidad: Mapped[str | None] = mapped_column(String(60), nullable=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)

    libros: Mapped[list[Libro]] = relationship(
        back_populates="autor",
        cascade="all, delete-orphan",
    )

    @property
    def nombre_completo(self) -> str:
        """Devuelve nombre y apellidos concatenados."""
        return f"{self.nombre} {self.apellidos}".strip()

    def __repr__(self) -> str:
        return (
            f"Autor(id_autor={self.id_autor!r}, "
            f"nombre={self.nombre!r}, apellidos={self.apellidos!r})"
        )
