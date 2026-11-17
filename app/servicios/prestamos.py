"""Servicio de aplicación para la gestión de préstamos y devoluciones."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta

from app.dto.prestamos import DatosPrestamo, PrestamoResumen
from app.excepciones import (
    EjemplarNoDisponible,
    EjemplarNoEncontrado,
    PrestamoNoEncontrado,
    PrestamoYaDevuelto,
    SocioInactivo,
    SocioNoEncontrado,
)
from app.modelos.prestamo import Prestamo
from app.unidad_trabajo import UnidadTrabajo


class PrestamoServicio:
    """Implementa los casos de uso de registro y devolución de préstamos."""

    def __init__(self, uow_factory: Callable[[], UnidadTrabajo]) -> None:
        self._uow_factory = uow_factory

    @staticmethod
    def _a_resumen(prestamo: Prestamo) -> PrestamoResumen:
        nombre_socio = (
            prestamo.socio.nombre_completo if prestamo.socio else f"Socio {prestamo.id_socio}"
        )
        codigos = [
            f"{ej.codigo_inventario} ({ej.libro.titulo})" if ej.libro else ej.codigo_inventario
            for ej in prestamo.ejemplares
        ]
        return PrestamoResumen(
            id_prestamo=prestamo.id_prestamo,
            socio=nombre_socio,
            fecha_prestamo=prestamo.fecha_prestamo,
            fecha_limite=prestamo.fecha_limite,
            fecha_devolucion=prestamo.fecha_devolucion,
            ejemplares=codigos,
        )

    def registrar_prestamo(
        self,
        datos: DatosPrestamo,
        fecha_actual: date | None = None,
    ) -> PrestamoResumen:
        """Registra un préstamo validando socio activo y ejemplar disponible."""
        hoy = fecha_actual or date.today()

        with self._uow_factory() as uow:
            socio = uow.socios.buscar(datos.id_socio)
            if socio is None:
                raise SocioNoEncontrado(f"No existe ningún socio con id {datos.id_socio}.")
            if not socio.activo:
                raise SocioInactivo(
                    f"El socio '{socio.nombre_completo}' está inactivo y no puede tomar préstamos."
                )

            ejemplar = uow.ejemplares.buscar(datos.id_ejemplar)
            if ejemplar is None:
                raise EjemplarNoEncontrado(
                    f"No existe ningún ejemplar con id {datos.id_ejemplar}."
                )
            if ejemplar.estado != "DISPONIBLE":
                raise EjemplarNoDisponible(
                    f"El ejemplar {ejemplar.codigo_inventario} no está disponible "
                    f"(estado actual: {ejemplar.estado})."
                )

            prestamo = Prestamo(
                id_socio=socio.id_socio,
                socio=socio,
                fecha_prestamo=hoy,
                fecha_limite=hoy + timedelta(days=datos.dias_plazo),
                observaciones=datos.observaciones,
            )
            prestamo.ejemplares.append(ejemplar)
            ejemplar.estado = "PRESTADO"

            uow.prestamos.anadir(prestamo)
            uow.flush()
            uow.commit()
            return self._a_resumen(prestamo)

    def devolver_prestamo(
        self,
        id_prestamo: int,
        fecha_devolucion: date | None = None,
    ) -> PrestamoResumen:
        """Registra la devolución de un préstamo y libera sus ejemplares."""
        fecha_cierre = fecha_devolucion or date.today()

        with self._uow_factory() as uow:
            prestamo = uow.prestamos.buscar(id_prestamo)
            if prestamo is None:
                raise PrestamoNoEncontrado(f"No existe ningún préstamo con id {id_prestamo}.")
            if prestamo.fecha_devolucion is not None:
                raise PrestamoYaDevuelto(
                    f"El préstamo {id_prestamo} ya fue devuelto el {prestamo.fecha_devolucion}."
                )

            prestamo.fecha_devolucion = fecha_cierre
            for ejemplar in prestamo.ejemplares:
                ejemplar.estado = "DISPONIBLE"

            uow.commit()
            return self._a_resumen(prestamo)

    def listar_prestamos_abiertos(self) -> list[PrestamoResumen]:
        """Devuelve la lista de préstamos pendientes de devolución."""
        with self._uow_factory() as uow:
            prestamos = uow.prestamos.listar_abiertos()
            return [self._a_resumen(p) for p in prestamos]
