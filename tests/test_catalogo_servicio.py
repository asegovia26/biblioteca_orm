"""Pruebas unitarias para CatalogoServicio usando repositorios y UoW falsos."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.dto.libros import DatosLibro, FiltroLibros
from app.excepciones import (
    AutorNoEncontrado,
    FiltroInvalido,
    IsbnDuplicado,
    LibroNoEncontrado,
    PrecioInvalido,
)
from app.servicios.catalogo import CatalogoServicio


@pytest.mark.parametrize("precio_invalido", [Decimal("-0.01"), Decimal("-15.00")])
def test_crear_libro_rechaza_precio_negativo(uow_falsa, precio_invalido: Decimal) -> None:
    servicio = CatalogoServicio(lambda: uow_falsa)
    datos = DatosLibro(
        isbn="978-84-000-0001-1",
        titulo="Libro inválido",
        precio=precio_invalido,
        id_autor=1,
    )

    with pytest.raises(PrecioInvalido):
        servicio.crear_libro(datos)

    assert not uow_falsa.confirmado


def test_crear_libro_rechaza_autor_inexistente(uow_falsa) -> None:
    servicio = CatalogoServicio(lambda: uow_falsa)
    datos = DatosLibro(
        isbn="978-84-000-0002-2",
        titulo="Libro sin autor",
        precio=Decimal("18.50"),
        id_autor=999,
    )

    with pytest.raises(AutorNoEncontrado):
        servicio.crear_libro(datos)

    assert not uow_falsa.confirmado


def test_crear_libro_rechaza_isbn_duplicado(uow_falsa) -> None:
    servicio = CatalogoServicio(lambda: uow_falsa)
    datos = DatosLibro(
        isbn="978-84-204-1214-6",
        titulo="Duplicado",
        precio=Decimal("20.00"),
        id_autor=1,
    )

    with pytest.raises(IsbnDuplicado):
        servicio.crear_libro(datos)

    assert not uow_falsa.confirmado


def test_crear_libro_correcto_confirma_uow(uow_falsa) -> None:
    servicio = CatalogoServicio(lambda: uow_falsa)
    datos = DatosLibro(
        isbn="978-84-999-1234-5",
        titulo="Novelas ejemplares",
        precio=Decimal("16.50"),
        id_autor=1,
    )

    resumen = servicio.crear_libro(datos)

    assert resumen.titulo == "Novelas ejemplares"
    assert resumen.autor == "Miguel de Cervantes"
    assert resumen.precio == Decimal("16.50")
    assert uow_falsa.confirmado


def test_actualizar_precio_y_desactivar_libro(uow_falsa) -> None:
    servicio = CatalogoServicio(lambda: uow_falsa)

    actualizado = servicio.actualizar_precio(1, Decimal("29.95"))
    assert actualizado.precio == Decimal("29.95")

    servicio.desactivar_libro(1)
    activos = servicio.listar_libros(FiltroLibros(solo_activos=True))
    assert all(l.id_libro != 1 for l in activos)


@pytest.mark.parametrize(
    "filtro",
    [
        FiltroLibros(pagina=0),
        FiltroLibros(tamano=0),
        FiltroLibros(precio_minimo=Decimal("30.00"), precio_maximo=Decimal("10.00")),
    ],
)
def test_listar_libros_rechaza_filtros_invalidos(uow_falsa, filtro: FiltroLibros) -> None:
    servicio = CatalogoServicio(lambda: uow_falsa)
    with pytest.raises(FiltroInvalido):
        servicio.listar_libros(filtro)


def test_buscar_libro_inexistente(uow_falsa) -> None:
    servicio = CatalogoServicio(lambda: uow_falsa)
    with pytest.raises(LibroNoEncontrado):
        servicio.buscar_libro(404)
