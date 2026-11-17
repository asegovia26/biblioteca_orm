"""Repositorio ORM para la entidad Socio."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modelos.socio import Socio


class SocioRepositorio:
    """Gestiona el acceso a datos de socios."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, id_socio: int) -> Socio | None:
        """Busca un socio por su identificador."""
        stmt = select(Socio).where(Socio.id_socio == id_socio)
        return self._session.scalars(stmt).first()

    def buscar_por_dni(self, dni: str) -> Socio | None:
        """Busca un socio por su DNI."""
        stmt = select(Socio).where(Socio.dni == dni)
        return self._session.scalars(stmt).first()

    def anadir(self, socio: Socio) -> None:
        """Añade un nuevo socio a la sesión actual."""
        self._session.add(socio)

    def listar(self, solo_activos: bool = True) -> list[Socio]:
        """Lista socios ordenados por apellidos y nombre."""
        stmt = select(Socio)
        if solo_activos:
            stmt = stmt.where(Socio.activo.is_(True))
        stmt = stmt.order_by(Socio.apellidos, Socio.nombre)
        return list(self._session.scalars(stmt).all())
