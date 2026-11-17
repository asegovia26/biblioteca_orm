"""Modelo ORM para la entidad Prestamo y tabla intermedia detalle_prestamo."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, Date, ForeignKey, Integer, SmallInteger, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.base import Base

if TYPE_CHECKING:
    from app.modelos.ejemplar import Ejemplar
    from app.modelos.socio import Socio


detalle_prestamo = Table(
    "detalle_prestamo",
    Base.metadata,
    Column(
        "id_prestamo",
        Integer,
        ForeignKey("prestamos.id_prestamo", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_ejemplar",
        Integer,
        ForeignKey("ejemplares.id_ejemplar", ondelete="RESTRICT"),
        primary_key=True,
    ),
    Column("renovaciones", SmallInteger, nullable=False, default=0),
)


class Prestamo(Base):
    """Representa un préstamo de uno o varios ejemplares a un socio."""

    __tablename__ = "prestamos"
    __table_args__ = (
        CheckConstraint("fecha_limite >= fecha_prestamo", name="ck_fechas_prestamo"),
        CheckConstraint(
            "fecha_devolucion IS NULL OR fecha_devolucion >= fecha_prestamo",
            name="ck_fecha_devolucion",
        ),
    )

    id_prestamo: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_socio: Mapped[int] = mapped_column(
        ForeignKey("socios.id_socio", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fecha_prestamo: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    fecha_limite: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fecha_devolucion: Mapped[date | None] = mapped_column(Date, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(String(250), nullable=True)

    socio: Mapped[Socio] = relationship(back_populates="prestamos")
    ejemplares: Mapped[list[Ejemplar]] = relationship(
        secondary=detalle_prestamo,
        back_populates="prestamos",
    )

    def __repr__(self) -> str:
        return (
            f"Prestamo(id_prestamo={self.id_prestamo!r}, id_socio={self.id_socio!r}, "
            f"fecha_prestamo={self.fecha_prestamo!r}, fecha_devolucion={self.fecha_devolucion!r})"
        )
