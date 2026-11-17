"""Repositorio ORM para la entidad Libro."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.dto.libros import FiltroLibros
from app.modelos.libro import Libro


class LibroRepositorio:
    """Gestiona el acceso a datos y consultas dinámicas de libros."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar(self, id_libro: int) -> Libro | None:
        """Busca un libro por su identificador cargando su autor."""
        stmt = (
            select(Libro)
            .options(joinedload(Libro.autor))
            .where(Libro.id_libro == id_libro)
        )
        return self._session.scalars(stmt).first()

    def buscar_por_isbn(self, isbn: str) -> Libro | None:
        """Busca un libro por su código ISBN."""
        stmt = select(Libro).where(Libro.isbn == isbn)
        return self._session.scalars(stmt).first()

    def anadir(self, libro: Libro) -> None:
        """Añade un nuevo libro a la sesión actual."""
        self._session.add(libro)

    def listar(self, filtro: FiltroLibros | None = None) -> list[Libro]:
        """Lista libros aplicando filtros dinámicos, paginación y carga de autor."""
        criterios = filtro or FiltroLibros()
        stmt = select(Libro).options(joinedload(Libro.autor))

        if criterios.solo_activos:
            stmt = stmt.where(Libro.activo.is_(True))
        if criterios.texto:
            patron = f"%{criterios.texto.strip()}%"
            stmt = stmt.where(Libro.titulo.ilike(patron))
        if criterios.id_autor is not None:
            stmt = stmt.where(Libro.id_autor == criterios.id_autor)
        if criterios.precio_minimo is not None:
            stmt = stmt.where(Libro.precio >= criterios.precio_minimo)
        if criterios.precio_maximo is not None:
            stmt = stmt.where(Libro.precio <= criterios.precio_maximo)

        desplazamiento = (criterios.pagina - 1) * criterios.tamano
        stmt = (
            stmt.order_by(Libro.id_libro)
            .offset(desplazamiento)
            .limit(criterios.tamano)
        )
        return list(self._session.scalars(stmt).all())
