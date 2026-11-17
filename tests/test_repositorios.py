"""Pruebas de integración contra PostgreSQL (base de datos biblioteca_test)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.dto.libros import FiltroLibros
from app.modelos import Autor, Ejemplar, Libro, Prestamo, Socio
from app.repositorios import (
    AutorRepositorio,
    EjemplarRepositorio,
    LibroRepositorio,
    PrestamoRepositorio,
    SocioRepositorio,
)


def test_insertar_y_recuperar_libro(sesion_test: Session) -> None:
    """Comprueba la inserción y recuperación de un libro con su autor."""
    autores = AutorRepositorio(sesion_test)
    libros = LibroRepositorio(sesion_test)

    autor = Autor(nombre="Gabriel", apellidos="García Márquez", nacionalidad="Colombiana")
    autores.anadir(autor)
    sesion_test.flush()

    libro = Libro(
        isbn="978-84-9759-220-8",
        titulo="Cien años de soledad",
        id_autor=autor.id_autor,
        precio=Decimal("14.95"),
        activo=True,
    )
    libros.anadir(libro)
    sesion_test.flush()
    sesion_test.expire_all()

    recuperado = libros.buscar(libro.id_libro)
    assert recuperado is not None
    assert recuperado.titulo == "Cien años de soledad"
    assert recuperado.precio == Decimal("14.95")
    assert recuperado.autor.nombre_completo == "Gabriel García Márquez"


def test_isbn_duplicado_lanza_integrity_error(sesion_test: Session) -> None:
    """Comprueba que la restricción UNIQUE sobre isbn impide duplicados."""
    autores = AutorRepositorio(sesion_test)
    libros = LibroRepositorio(sesion_test)

    autor = Autor(nombre="Isabel", apellidos="Allende", nacionalidad="Chilena")
    autores.anadir(autor)
    sesion_test.flush()

    libros.anadir(
        Libro(
            isbn="978-84-204-8247-7",
            titulo="La casa de los espíritus",
            id_autor=autor.id_autor,
            precio=Decimal("19.90"),
        )
    )
    sesion_test.flush()

    libros.anadir(
        Libro(
            isbn="978-84-204-8247-7",
            titulo="Otro título con mismo ISBN",
            id_autor=autor.id_autor,
            precio=Decimal("15.00"),
        )
    )

    with pytest.raises(IntegrityError):
        sesion_test.flush()


def test_registrar_prestamo_y_comprobar_estado_ejemplar(sesion_test: Session) -> None:
    """Comprueba el registro de un préstamo y la actualización de estado del ejemplar."""
    autores = AutorRepositorio(sesion_test)
    libros = LibroRepositorio(sesion_test)
    ejemplares = EjemplarRepositorio(sesion_test)
    socios = SocioRepositorio(sesion_test)
    prestamos = PrestamoRepositorio(sesion_test)

    autor = Autor(nombre="Julio", apellidos="Verne", nacionalidad="Francesa")
    autores.anadir(autor)
    sesion_test.flush()

    libro = Libro(
        isbn="978-84-9104-356-0",
        titulo="Viaje al centro de la Tierra",
        id_autor=autor.id_autor,
        precio=Decimal("13.75"),
    )
    libros.anadir(libro)
    sesion_test.flush()

    ejemplar = Ejemplar(
        id_libro=libro.id_libro,
        codigo_inventario="EJ-TEST-01",
        ubicacion="A2-01",
        estado="DISPONIBLE",
    )
    ejemplares.anadir(ejemplar)

    socio = Socio(
        dni="99999999Z",
        nombre="Lucía",
        apellidos="Torres Martín",
        email="lucia.test@example.test",
        activo=True,
    )
    socios.anadir(socio)
    sesion_test.flush()

    hoy = date(2026, 11, 1)
    prestamo = Prestamo(
        id_socio=socio.id_socio,
        fecha_prestamo=hoy,
        fecha_limite=hoy + timedelta(days=14),
    )
    prestamo.ejemplares.append(ejemplar)
    ejemplar.estado = "PRESTADO"
    prestamos.anadir(prestamo)
    sesion_test.flush()
    sesion_test.expire_all()

    prestamo_bd = prestamos.buscar(prestamo.id_prestamo)
    ejemplar_bd = ejemplares.buscar(ejemplar.id_ejemplar)

    assert prestamo_bd is not None
    assert prestamo_bd.socio.dni == "99999999Z"
    assert len(prestamo_bd.ejemplares) == 1
    assert ejemplar_bd is not None
    assert ejemplar_bd.estado == "PRESTADO"


def test_consulta_dinamica_filtros_y_paginacion(sesion_test: Session) -> None:
    """Verifica el filtrado combinado por texto, precio y paginación."""
    autores = AutorRepositorio(sesion_test)
    libros = LibroRepositorio(sesion_test)

    autor = Autor(nombre="Robert C.", apellidos="Martin", nacionalidad="Estadounidense")
    autores.anadir(autor)
    sesion_test.flush()

    for idx in range(1, 6):
        libros.anadir(
            Libro(
                isbn=f"978-01-323-000{idx}-0",
                titulo=f"Arquitectura Limpia Vol. {idx}",
                id_autor=autor.id_autor,
                precio=Decimal("10.00") * idx,
                activo=True,
            )
        )
    sesion_test.flush()

    filtro = FiltroLibros(
        texto="Arquitectura",
        precio_minimo=Decimal("20.00"),
        precio_maximo=Decimal("40.00"),
        pagina=1,
        tamano=2,
    )
    pagina_1 = libros.listar(filtro)
    assert len(pagina_1) == 2
    assert all(Decimal("20.00") <= l.precio <= Decimal("40.00") for l in pagina_1)


def test_evita_problema_n_mas_1_con_selectinload(sesion_test: Session) -> None:
    """Demuestra la reducción de consultas SQL usando selectinload en autores->libros."""
    autores_repo = AutorRepositorio(sesion_test)
    libros_repo = LibroRepositorio(sesion_test)

    for i in range(1, 6):
        autor = Autor(nombre=f"Autor{i}", apellidos="Prueba")
        autores_repo.anadir(autor)
        sesion_test.flush()
        libros_repo.anadir(
            Libro(
                isbn=f"978-84-100-000{i}-0",
                titulo=f"Libro {i}",
                id_autor=autor.id_autor,
                precio=Decimal("15.00"),
            )
        )
    sesion_test.flush()
    sesion_test.expire_all()

    consultas: list[str] = []

    def contar_sql(conn, cursor, statement, parameters, context, executemany):
        consultas.append(statement)

    motor = sesion_test.get_bind()
    event.listen(motor, "before_cursor_execute", contar_sql)
    try:
        # Sin optimización (carga perezosa)
        consultas.clear()
        autores_lazy = list(sesion_test.scalars(select(Autor)).all())
        _ = [len(a.libros) for a in autores_lazy]
        total_sin_optimizar = len(consultas)

        sesion_test.expire_all()

        # Con selectinload
        consultas.clear()
        autores_opt = list(
            sesion_test.scalars(select(Autor).options(selectinload(Autor.libros))).all()
        )
        _ = [len(a.libros) for a in autores_opt]
        total_optimizado = len(consultas)
    finally:
        event.remove(motor, "before_cursor_execute", contar_sql)

    assert total_sin_optimizar == 6  # 1 consulta de autores + 5 de libros
    assert total_optimizado == 2     # 1 consulta de autores + 1 agrupada de libros
