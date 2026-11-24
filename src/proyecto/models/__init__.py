"""Modelos de la aplicación.

Importá acá cada modelo para que SQLAlchemy lo registre en db.metadata
(y Flask-Migrate lo detecte) antes de configurar los mappers.
"""

from proyecto.models import Administrator as Administrator
from proyecto.models import Category as Category
from proyecto.models import Moderator as Moderator
from proyecto.models import RegularUser as RegularUser
from proyecto.models import User as User
from proyecto.models import Post as Post
from proyecto.models import Question as Question
from proyecto.models import Tag as Tag
from proyecto.models import QuestionTag as QuestionTag
