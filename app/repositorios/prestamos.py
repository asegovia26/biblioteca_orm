"""Repositorio ORM para la entidad Prestamo."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modelos.ejemplar import Ejemplar
from app.modelos.prestamo import Prestamo


class PrestamoRepositorio:
    """Gestiona el acceso a datos de préstamos."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, id_prestamo: int) -> Prestamo | None:
        """Busca un préstamo por su identificador cargando socio y ejemplares."""
        stmt = (
            select(Prestamo)
            .options(
                joinedload(Prestamo.socio),
                selectinload(Prestamo.ejemplares).joinedload(Ejemplar.libro),
            )
            .where(Prestamo.id_prestamo == id_prestamo)
        )
        return self._session.scalars(stmt).first()

    def anadir(self, prestamo: Prestamo) -> None:
        """Añade un nuevo préstamo a la sesión actual."""
        self._session.add(prestamo)

    def listar_abiertos(self) -> list[Prestamo]:
        """Lista los préstamos aún no devueltos evitando consultas N+1."""
        stmt = (
            select(Prestamo)
            .options(
                joinedload(Prestamo.socio),
                selectinload(Prestamo.ejemplares).joinedload(Ejemplar.libro),
            )
            .where(Prestamo.fecha_devolucion.is_(None))
            .order_by(Prestamo.fecha_limite, Prestamo.id_prestamo)
        )
        return list(self._session.scalars(stmt).all())
