"""Modelos de la aplicación.

Importá acá cada modelo, por ejemplo:

    from models.user import User

Así SQLAlchemy los registra en db.metadata (y Flask-Migrate los detecta)
antes de configurar los mappers.
"""
from proyecto.models import Category as Category
from proyecto.models import User as User
