"""Excepciones de dominio de la aplicación Biblioteca ORM."""


class ErrorBiblioteca(Exception):
    """Excepción base para errores de negocio de la biblioteca."""


class AutorNoEncontrado(ErrorBiblioteca):
    """Se lanza cuando no existe el autor solicitado."""


class LibroNoEncontrado(ErrorBiblioteca):
    """Se lanza cuando no existe el libro solicitado."""


class IsbnDuplicado(ErrorBiblioteca):
    """Se lanza al intentar registrar un ISBN ya existente."""


class PrecioInvalido(ErrorBiblioteca):
    """Se lanza cuando el precio de un libro es negativo o inválido."""


class FiltroInvalido(ErrorBiblioteca):
    """Se lanza cuando los parámetros de filtrado o paginación son inválidos."""


class SocioNoEncontrado(ErrorBiblioteca):
    """Se lanza cuando no existe el socio solicitado."""


class SocioInactivo(ErrorBiblioteca):
    """Se lanza cuando un socio inactivo intenta realizar un préstamo."""


class EjemplarNoEncontrado(ErrorBiblioteca):
    """Se lanza cuando no existe el ejemplar solicitado."""


class EjemplarNoDisponible(ErrorBiblioteca):
    """Se lanza cuando el ejemplar no está en estado DISPONIBLE."""


class PrestamoNoEncontrado(ErrorBiblioteca):
    """Se lanza cuando no existe el préstamo solicitado."""


class PrestamoYaDevuelto(ErrorBiblioteca):
    """Se lanza cuando se intenta devolver un préstamo ya cerrado."""
