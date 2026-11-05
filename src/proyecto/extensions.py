from flask import current_app, g
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.pool import StaticPool

# Importante usar StaticPool para sqlite en memoria, hace que todas las sesiones compartan la misma base de datos, sino se crearía una base de datos diferente por cada test.

class Base(DeclarativeBase):
    """Base declarativa de la que heredan todos los modelos."""


def create_db_engine(url: str) -> Engine:
    """Crea el engine de SQLAlchemy a partir de la URL de config.py."""
    kwargs = {}
    if url.endswith(":memory:"):
        # SQLite en memoria: todos los pedidos comparten la misma conexión
        kwargs = {
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False},
        }
    return create_engine(url, **kwargs)


def get_session() -> Session:
    """Devuelve la sesión del request actual (se crea si no existe)."""
    if "db" not in g:
        g.db = current_app.extensions["db_session"]()
    return g.db
