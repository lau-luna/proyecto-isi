from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from proyecto.extensions import db

class User(db.Model):
    # nombre de tabla
    __tablename__ = "user"

    # atributos de la tabla
    id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
