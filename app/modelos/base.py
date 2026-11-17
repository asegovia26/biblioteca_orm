"""Base declarativa compartida para los modelos ORM."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Clase base para todas las entidades ORM de SQLAlchemy."""
