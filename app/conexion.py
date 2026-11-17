"""Gestión de la conexión a PostgreSQL y fábrica de sesiones SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.configuracion import cargar_configuracion


def crear_motor(database_url: str | None = None, echo: bool | None = None) -> Engine:
    """Crea un Engine de SQLAlchemy 2.x para la URL indicada."""
    config = cargar_configuracion()
    url = database_url or config.database_url
    mostrar_sql = config.sql_echo if echo is None else echo
    return create_engine(url, echo=mostrar_sql, future=True)


def crear_fabrica_sesiones(motor: Engine | None = None) -> sessionmaker[Session]:
    """Crea un sessionmaker configurado con expire_on_commit=False."""
    engine = motor or crear_motor()
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
