"""Configuración de la aplicación mediante variables de entorno."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Configuracion:
    """Almacena los parámetros de conexión y ejecución."""

    database_url: str
    test_database_url: str
    sql_echo: bool = False


def cargar_configuracion() -> Configuracion:
    """Carga la configuración desde variables de entorno sin credenciales fijas."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://localhost:5432/biblioteca_orm",
    )
    test_database_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://localhost:5432/biblioteca_test",
    )
    sql_echo = os.getenv("SQL_ECHO", "false").lower() in ("1", "true", "yes")
    return Configuracion(
        database_url=database_url,
        test_database_url=test_database_url,
        sql_echo=sql_echo,
    )
