from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from proyecto.extensions import db

class User(db.Model):
    # nombre de tabla
    __tablename__ = "user"

    # atributos de la tabla
    id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)

    def __init__(self, username:str, email:str, password_hash:str) -> None:
        self.username = username
        self.email = email
        self.password_hash = password_hash

    # Author interface
    def get_display_name(self) -> str:
        return self.username
