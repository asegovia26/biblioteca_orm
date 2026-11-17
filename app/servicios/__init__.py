"""Servicios de aplicación y lógica de negocio."""

from app.servicios.catalogo import CatalogoServicio
from app.servicios.prestamos import PrestamoServicio

__all__ = ["CatalogoServicio", "PrestamoServicio"]
