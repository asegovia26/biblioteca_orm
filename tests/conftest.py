"""Fixtures compartidas para pruebas unitarias (UoW falsa) e integración (biblioteca_test)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.configuracion import cargar_configuracion
from app.conexion import crear_motor
from app.dto.libros import FiltroLibros
from app.modelos import Autor, Base, Ejemplar, Libro, Prestamo, Socio


class AutorRepoFalso:
    """Repositorio en memoria para autores."""

    def __init__(self, datos: dict[int, Autor] | None = None) -> None:
        self._datos: dict[int, Autor] = datos or {}
        self._seq = max(self._datos.keys(), default=0)

    def buscar(self, id_autor: int) -> Autor | None:
        return self._datos.get(id_autor)

    def anadir(self, autor: Autor) -> None:
        if autor.id_autor is None:
            self._seq += 1
            autor.id_autor = self._seq
        self._datos[autor.id_autor] = autor

    def listar(self, cargar_libros: bool = True) -> list[Autor]:
        return list(self._datos.values())


class LibroRepoFalso:
    """Repositorio en memoria para libros."""

    def __init__(self, datos: dict[int, Libro] | None = None) -> None:
        self._datos: dict[int, Libro] = datos or {}
        self._seq = max(self._datos.keys(), default=0)

    def buscar(self, id_libro: int) -> Libro | None:
        return self._datos.get(id_libro)

    def buscar_por_isbn(self, isbn: str) -> Libro | None:
        return next((l for l in self._datos.values() if l.isbn == isbn), None)

    def anadir(self, libro: Libro) -> None:
        if libro.id_libro is None:
            self._seq += 1
            libro.id_libro = self._seq
        self._datos[libro.id_libro] = libro

    def listar(self, filtro: FiltroLibros | None = None) -> list[Libro]:
        criterios = filtro or FiltroLibros()
        resultado = list(self._datos.values())
        if criterios.solo_activos:
            resultado = [l for l in resultado if l.activo]
        if criterios.texto:
            texto = criterios.texto.lower()
            resultado = [l for l in resultado if texto in l.titulo.lower()]
        if criterios.id_autor is not None:
            resultado = [l for l in resultado if l.id_autor == criterios.id_autor]
        if criterios.precio_minimo is not None:
            resultado = [l for l in resultado if l.precio >= criterios.precio_minimo]
        if criterios.precio_maximo is not None:
            resultado = [l for l in resultado if l.precio <= criterios.precio_maximo]
        inicio = (criterios.pagina - 1) * criterios.tamano
        return resultado[inicio : inicio + criterios.tamano]


class SocioRepoFalso:
    """Repositorio en memoria para socios."""

    def __init__(self, datos: dict[int, Socio] | None = None) -> None:
        self._datos: dict[int, Socio] = datos or {}

    def buscar(self, id_socio: int) -> Socio | None:
        return self._datos.get(id_socio)

    def anadir(self, socio: Socio) -> None:
        self._datos[socio.id_socio] = socio


class EjemplarRepoFalso:
    """Repositorio en memoria para ejemplares."""

    def __init__(self, datos: dict[int, Ejemplar] | None = None) -> None:
        self._datos: dict[int, Ejemplar] = datos or {}

    def buscar(self, id_ejemplar: int) -> Ejemplar | None:
        return self._datos.get(id_ejemplar)

    def anadir(self, ejemplar: Ejemplar) -> None:
        self._datos[ejemplar.id_ejemplar] = ejemplar


class PrestamoRepoFalso:
    """Repositorio en memoria para préstamos."""

    def __init__(self, datos: dict[int, Prestamo] | None = None) -> None:
        self._datos: dict[int, Prestamo] = datos or {}
        self._seq = max(self._datos.keys(), default=0)

    def buscar(self, id_prestamo: int) -> Prestamo | None:
        return self._datos.get(id_prestamo)

    def anadir(self, prestamo: Prestamo) -> None:
        if prestamo.id_prestamo is None:
            self._seq += 1
            prestamo.id_prestamo = self._seq
        self._datos[prestamo.id_prestamo] = prestamo

    def listar_abiertos(self) -> list[Prestamo]:
        return [p for p in self._datos.values() if p.fecha_devolucion is None]


class UnidadTrabajoFalsa:
    """Unit of Work en memoria que registra llamadas a commit/rollback/flush."""

    def __init__(
        self,
        autores: AutorRepoFalso,
        libros: LibroRepoFalso,
        socios: SocioRepoFalso,
        ejemplares: EjemplarRepoFalso,
        prestamos: PrestamoRepoFalso,
    ) -> None:
        self.autores = autores
        self.libros = libros
        self.socios = socios
        self.ejemplares = ejemplares
        self.prestamos = prestamos
        self.confirmado = False
        self.revertido = False
        self.flushed = False

    def __enter__(self) -> UnidadTrabajoFalsa:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()

    def flush(self) -> None:
        self.flushed = True

    def commit(self) -> None:
        self.confirmado = True

    def rollback(self) -> None:
        self.revertido = True


@pytest.fixture
def uow_falsa() -> UnidadTrabajoFalsa:
    """Proporciona una Unit of Work en memoria con datos iniciales de prueba."""
    autor1 = Autor(id_autor=1, nombre="Miguel", apellidos="de Cervantes", nacionalidad="Española")
    autor2 = Autor(id_autor=2, nombre="George", apellidos="Orwell", nacionalidad="Británica")

    libro1 = Libro(
        id_libro=1,
        isbn="978-84-204-1214-6",
        titulo="Don Quijote de la Mancha",
        id_autor=1,
        autor=autor1,
        precio=Decimal("24.90"),
        activo=True,
    )
    libro2 = Libro(
        id_libro=2,
        isbn="978-84-206-0925-5",
        titulo="1984",
        id_autor=2,
        autor=autor2,
        precio=Decimal("12.95"),
        activo=True,
    )
    libro_inactivo = Libro(
        id_libro=3,
        isbn="978-00-000-0000-0",
        titulo="Libro descatalogado",
        id_autor=2,
        autor=autor2,
        precio=Decimal("9.99"),
        activo=False,
    )

    socio_activo = Socio(
        id_socio=1,
        dni="10000001A",
        nombre="Ana",
        apellidos="Martín López",
        email="ana@example.test",
        activo=True,
    )
    socio_inactivo = Socio(
        id_socio=2,
        dni="10000008H",
        nombre="Pablo",
        apellidos="Ortega León",
        email="pablo@example.test",
        activo=False,
    )

    ejemplar_disponible = Ejemplar(
        id_ejemplar=1,
        id_libro=1,
        libro=libro1,
        codigo_inventario="EJ-0001",
        ubicacion="A1-01",
        estado="DISPONIBLE",
    )
    ejemplar_prestado = Ejemplar(
        id_ejemplar=2,
        id_libro=2,
        libro=libro2,
        codigo_inventario="EJ-0002",
        ubicacion="A1-02",
        estado="PRESTADO",
    )

    prestamo_abierto = Prestamo(
        id_prestamo=1,
        id_socio=1,
        socio=socio_activo,
        fecha_prestamo=date(2026, 10, 1),
        fecha_limite=date(2026, 10, 15),
        fecha_devolucion=None,
        ejemplares=[ejemplar_prestado],
    )

    return UnidadTrabajoFalsa(
        autores=AutorRepoFalso({1: autor1, 2: autor2}),
        libros=LibroRepoFalso({1: libro1, 2: libro2, 3: libro_inactivo}),
        socios=SocioRepoFalso({1: socio_activo, 2: socio_inactivo}),
        ejemplares=EjemplarRepoFalso({1: ejemplar_disponible, 2: ejemplar_prestado}),
        prestamos=PrestamoRepoFalso({1: prestamo_abierto}),
    )


@pytest.fixture(scope="session")
def motor_test():
    """Motor SQLAlchemy conectado a biblioteca_test con esquema recreado."""
    config = cargar_configuracion()
    motor = crear_motor(config.test_database_url, echo=False)
    Base.metadata.drop_all(motor)
    Base.metadata.create_all(motor)
    yield motor
    Base.metadata.drop_all(motor)
    motor.dispose()


@pytest.fixture
def sesion_test(motor_test) -> Session:
    """Proporciona una sesión envuelta en transacción que se revierte al finalizar cada test."""
    conexion = motor_test.connect()
    transaccion = conexion.begin()
    fabrica = sessionmaker(bind=conexion, autoflush=False, expire_on_commit=False)
    sesion = fabrica()
    try:
        yield sesion
    finally:
        sesion.close()
        if transaccion.is_active:
            transaccion.rollback()
        conexion.close()
