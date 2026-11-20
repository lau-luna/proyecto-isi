"""Modelos de la aplicación.

Importá acá cada modelo para que SQLAlchemy lo registre en db.metadata
(y Flask-Migrate lo detecte) antes de configurar los mappers.
"""

from proyecto.models import Category as Category
from proyecto.models import RegularUser as RegularUser
from proyecto.models import User as User
