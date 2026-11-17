"""Repositorio ORM para la entidad Ejemplar."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modelos.ejemplar import Ejemplar


class EjemplarRepositorio:
    """Gestiona el acceso a datos de ejemplares."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, id_ejemplar: int) -> Ejemplar | None:
        """Busca un ejemplar por su identificador cargando el libro asociado."""
        stmt = (
            select(Ejemplar)
            .options(joinedload(Ejemplar.libro))
            .where(Ejemplar.id_ejemplar == id_ejemplar)
        )
        return self._session.scalars(stmt).first()

    def buscar_por_codigo(self, codigo_inventario: str) -> Ejemplar | None:
        """Busca un ejemplar por su código de inventario."""
        stmt = select(Ejemplar).where(Ejemplar.codigo_inventario == codigo_inventario)
        return self._session.scalars(stmt).first()

    def anadir(self, ejemplar: Ejemplar) -> None:
        """Añade un nuevo ejemplar a la sesión actual."""
        self._session.add(ejemplar)

    def listar(self, solo_disponibles: bool = False) -> list[Ejemplar]:
        """Lista ejemplares con su libro asociado."""
        stmt = select(Ejemplar).options(joinedload(Ejemplar.libro))
        if solo_disponibles:
            stmt = stmt.where(Ejemplar.estado == "DISPONIBLE")
        stmt = stmt.order_by(Ejemplar.id_ejemplar)
        return list(self._session.scalars(stmt).all())
