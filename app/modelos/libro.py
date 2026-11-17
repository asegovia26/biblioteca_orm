"""Modelo ORM para la entidad Libro."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.base import Base

if TYPE_CHECKING:
    from app.modelos.autor import Autor
    from app.modelos.ejemplar import Ejemplar


class Libro(Base):
    """Representa un libro del catálogo de la biblioteca."""

    __tablename__ = "libros"
    __table_args__ = (
        CheckConstraint("precio >= 0", name="ck_libro_precio_no_negativo"),
        CheckConstraint("paginas IS NULL OR paginas > 0", name="ck_libro_paginas_positivas"),
        CheckConstraint(
            "anio_publicacion IS NULL OR anio_publicacion BETWEEN 1450 AND 2100",
            name="ck_anio_publicacion",
        ),
    )

    id_libro: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    titulo: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    id_autor: Mapped[int] = mapped_column(
        ForeignKey("autores.id_autor", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    anio_publicacion: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    paginas: Mapped[int | None] = mapped_column(nullable=True)
    idioma: Mapped[str] = mapped_column(String(40), nullable=False, default="Español")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    observaciones: Mapped[str | None] = mapped_column(String(500), nullable=True)

    autor: Mapped[Autor] = relationship(back_populates="libros")
    ejemplares: Mapped[list[Ejemplar]] = relationship(
        back_populates="libro",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"Libro(id_libro={self.id_libro!r}, isbn={self.isbn!r}, "
            f"titulo={self.titulo!r}, precio={self.precio!r}, activo={self.activo!r})"
        )
