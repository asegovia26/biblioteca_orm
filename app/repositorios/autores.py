"""Repositorio ORM para la entidad Autor."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modelos.autor import Autor


class AutorRepositorio:
    """Gestiona el acceso a datos de autores."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, id_autor: int) -> Autor | None:
        """Busca un autor por su identificador."""
        stmt = select(Autor).where(Autor.id_autor == id_autor)
        return self._session.scalars(stmt).first()

    def anadir(self, autor: Autor) -> None:
        """Añade un nuevo autor a la sesión actual."""
        self._session.add(autor)

    def listar(self, cargar_libros: bool = True) -> list[Autor]:
        """Lista todos los autores ordenados por apellidos y nombre."""
        stmt = select(Autor).order_by(Autor.apellidos, Autor.nombre)
        if cargar_libros:
            stmt = stmt.options(selectinload(Autor.libros))
        return list(self._session.scalars(stmt).all())
