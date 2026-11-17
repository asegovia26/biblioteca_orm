"""Modelo ORM para la entidad Ejemplar."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.base import Base

if TYPE_CHECKING:
    from app.modelos.libro import Libro
    from app.modelos.prestamo import Prestamo


class Ejemplar(Base):
    """Representa una copia física de un libro en la biblioteca."""

    __tablename__ = "ejemplares"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('DISPONIBLE', 'PRESTADO', 'RESERVADO', 'BAJA')",
            name="ck_estado_ejemplar",
        ),
    )

    id_ejemplar: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_libro: Mapped[int] = mapped_column(
        ForeignKey("libros.id_libro", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    codigo_inventario: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(40), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="DISPONIBLE")
    fecha_alta: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    libro: Mapped[Libro] = relationship(back_populates="ejemplares")
    prestamos: Mapped[list[Prestamo]] = relationship(
        secondary="detalle_prestamo",
        back_populates="ejemplares",
    )

    def __repr__(self) -> str:
        return (
            f"Ejemplar(id_ejemplar={self.id_ejemplar!r}, "
            f"codigo={self.codigo_inventario!r}, estado={self.estado!r})"
        )
