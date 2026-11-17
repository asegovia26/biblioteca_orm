"""Exportación de los repositorios ORM."""

from app.repositorios.autores import AutorRepositorio
from app.repositorios.ejemplares import EjemplarRepositorio
from app.repositorios.libros import LibroRepositorio
from app.repositorios.prestamos import PrestamoRepositorio
from app.repositorios.socios import SocioRepositorio

__all__ = [
    "AutorRepositorio",
    "LibroRepositorio",
    "SocioRepositorio",
    "EjemplarRepositorio",
    "PrestamoRepositorio",
]
