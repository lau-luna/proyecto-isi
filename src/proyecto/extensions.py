from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa de la que heredan todos los modelos."""


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
