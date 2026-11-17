"""Pruebas unitarias para PrestamoServicio usando repositorios y UoW falsos."""

from __future__ import annotations

from datetime import date

import pytest

from app.dto.prestamos import DatosPrestamo
from app.excepciones import (
    EjemplarNoDisponible,
    EjemplarNoEncontrado,
    PrestamoNoEncontrado,
    PrestamoYaDevuelto,
    SocioInactivo,
    SocioNoEncontrado,
)
from app.servicios.prestamos import PrestamoServicio


def test_registrar_prestamo_rechaza_socio_inactivo(uow_falsa) -> None:
    servicio = PrestamoServicio(lambda: uow_falsa)
    datos = DatosPrestamo(id_socio=2, id_ejemplar=1)

    with pytest.raises(SocioInactivo):
        servicio.registrar_prestamo(datos)

    assert not uow_falsa.confirmado


def test_registrar_prestamo_rechaza_socio_inexistente(uow_falsa) -> None:
    servicio = PrestamoServicio(lambda: uow_falsa)
    with pytest.raises(SocioNoEncontrado):
        servicio.registrar_prestamo(DatosPrestamo(id_socio=999, id_ejemplar=1))


def test_registrar_prestamo_rechaza_ejemplar_no_disponible(uow_falsa) -> None:
    servicio = PrestamoServicio(lambda: uow_falsa)
    datos = DatosPrestamo(id_socio=1, id_ejemplar=2)

    with pytest.raises(EjemplarNoDisponible):
        servicio.registrar_prestamo(datos)

    assert not uow_falsa.confirmado


def test_registrar_prestamo_rechaza_ejemplar_inexistente(uow_falsa) -> None:
    servicio = PrestamoServicio(lambda: uow_falsa)
    with pytest.raises(EjemplarNoEncontrado):
        servicio.registrar_prestamo(DatosPrestamo(id_socio=1, id_ejemplar=999))


def test_registrar_y_devolver_prestamo_correctamente(uow_falsa) -> None:
    servicio = PrestamoServicio(lambda: uow_falsa)
    datos = DatosPrestamo(id_socio=1, id_ejemplar=1, dias_plazo=14)

    creado = servicio.registrar_prestamo(datos, fecha_actual=date(2026, 11, 1))
    assert creado.socio == "Ana Martín López"
    assert creado.fecha_limite == date(2026, 11, 15)
    assert uow_falsa.ejemplares.buscar(1).estado == "PRESTADO"
    assert uow_falsa.confirmado

    devuelto = servicio.devolver_prestamo(creado.id_prestamo, fecha_devolucion=date(2026, 11, 10))
    assert devuelto.fecha_devolucion == date(2026, 11, 10)
    assert uow_falsa.ejemplares.buscar(1).estado == "DISPONIBLE"


def test_devolver_prestamo_ya_cerrado_lanza_excepcion(uow_falsa) -> None:
    servicio = PrestamoServicio(lambda: uow_falsa)

    servicio.devolver_prestamo(1, fecha_devolucion=date(2026, 10, 10))
    with pytest.raises(PrestamoYaDevuelto):
        servicio.devolver_prestamo(1, fecha_devolucion=date(2026, 10, 11))


def test_devolver_prestamo_inexistente_lanza_excepcion(uow_falsa) -> None:
    servicio = PrestamoServicio(lambda: uow_falsa)
    with pytest.raises(PrestamoNoEncontrado):
        servicio.devolver_prestamo(999)
