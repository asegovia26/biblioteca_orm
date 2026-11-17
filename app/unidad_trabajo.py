"""Implementación del patrón Unit of Work sobre SQLAlchemy Session."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType

from sqlalchemy.orm import Session

from app.repositorios.autores import AutorRepositorio
from app.repositorios.ejemplares import EjemplarRepositorio
from app.repositorios.libros import LibroRepositorio
from app.repositorios.prestamos import PrestamoRepositorio
from app.repositorios.socios import SocioRepositorio


class UnidadTrabajo:
    """Coordina repositorios bajo una única sesión y transacción."""

    autores: AutorRepositorio
    libros: LibroRepositorio
    socios: SocioRepositorio
    ejemplares: EjemplarRepositorio
    prestamos: PrestamoRepositorio

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> UnidadTrabajo:
        self._session = self._session_factory()
        self.autores = AutorRepositorio(self._session)
        self.libros = LibroRepositorio(self._session)
        self.socios = SocioRepositorio(self._session)
        self.ejemplares = EjemplarRepositorio(self._session)
        self.prestamos = PrestamoRepositorio(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self._session.close()
            self._session = None

    def flush(self) -> None:
        """Envía los cambios pendientes a la base de datos sin confirmar."""
        if self._session is not None:
            self._session.flush()

    def commit(self) -> None:
        """Confirma la transacción actual."""
        if self._session is not None:
            self._session.commit()

    def rollback(self) -> None:
        """Revierte la transacción actual."""
        if self._session is not None:
            self._session.rollback()
