"""Servicio de aplicación para la gestión del catálogo de libros."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

from app.dto.libros import DatosLibro, FiltroLibros, LibroResumen
from app.excepciones import (
    AutorNoEncontrado,
    FiltroInvalido,
    IsbnDuplicado,
    LibroNoEncontrado,
    PrecioInvalido,
)
from app.modelos.libro import Libro
from app.unidad_trabajo import UnidadTrabajo


class CatalogoServicio:
    """Implementa los casos de uso del catálogo de libros."""

    def __init__(self, uow_factory: Callable[[], UnidadTrabajo]) -> None:
        self._uow_factory = uow_factory

    @staticmethod
    def _a_resumen(libro: Libro) -> LibroResumen:
        autor_nombre = libro.autor.nombre_completo if libro.autor else "Desconocido"
        return LibroResumen(
            id_libro=libro.id_libro,
            titulo=libro.titulo,
            autor=autor_nombre,
            precio=libro.precio,
        )

    @staticmethod
    def _validar_precio(precio: Decimal) -> None:
        if precio < Decimal("0"):
            raise PrecioInvalido("El precio del libro no puede ser negativo.")

    @staticmethod
    def _validar_filtro(filtro: FiltroLibros) -> None:
        if filtro.pagina < 1 or filtro.tamano < 1:
            raise FiltroInvalido("La página y el tamaño deben ser mayores o iguales que 1.")
        if (
            filtro.precio_minimo is not None
            and filtro.precio_maximo is not None
            and filtro.precio_minimo > filtro.precio_maximo
        ):
            raise FiltroInvalido("El precio mínimo no puede superar al precio máximo.")

    def listar_libros(self, filtro: FiltroLibros | None = None) -> list[LibroResumen]:
        """Lista libros aplicando filtros dinámicos y paginación."""
        criterios = filtro or FiltroLibros()
        self._validar_filtro(criterios)

        with self._uow_factory() as uow:
            libros = uow.libros.listar(criterios)
            return [self._a_resumen(libro) for libro in libros]

    def buscar_libro(self, id_libro: int) -> LibroResumen:
        """Busca un libro por su identificador."""
        with self._uow_factory() as uow:
            libro = uow.libros.buscar(id_libro)
            if libro is None:
                raise LibroNoEncontrado(f"No existe ningún libro con id {id_libro}.")
            return self._a_resumen(libro)

    def crear_libro(self, datos: DatosLibro) -> LibroResumen:
        """Crea un nuevo libro validando precio, autor e ISBN único."""
        self._validar_precio(datos.precio)

        with self._uow_factory() as uow:
            autor = uow.autores.buscar(datos.id_autor)
            if autor is None:
                raise AutorNoEncontrado(f"No existe ningún autor con id {datos.id_autor}.")

            existente = uow.libros.buscar_por_isbn(datos.isbn)
            if existente is not None:
                raise IsbnDuplicado(f"Ya existe un libro con el ISBN {datos.isbn}.")

            libro = Libro(
                isbn=datos.isbn.strip(),
                titulo=datos.titulo.strip(),
                precio=datos.precio,
                id_autor=datos.id_autor,
                autor=autor,
                activo=True,
            )
            uow.libros.anadir(libro)
            uow.flush()
            uow.commit()
            return self._a_resumen(libro)

    def actualizar_precio(self, id_libro: int, nuevo_precio: Decimal) -> LibroResumen:
        """Actualiza el precio de un libro existente."""
        self._validar_precio(nuevo_precio)

        with self._uow_factory() as uow:
            libro = uow.libros.buscar(id_libro)
            if libro is None:
                raise LibroNoEncontrado(f"No existe ningún libro con id {id_libro}.")

            libro.precio = nuevo_precio
            uow.commit()
            return self._a_resumen(libro)

    def desactivar_libro(self, id_libro: int) -> None:
        """Realiza la eliminación lógica de un libro."""
        with self._uow_factory() as uow:
            libro = uow.libros.buscar(id_libro)
            if libro is None:
                raise LibroNoEncontrado(f"No existe ningún libro con id {id_libro}.")

            libro.activo = False
            uow.commit()
