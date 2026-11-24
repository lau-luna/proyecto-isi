from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.extensions import db
from proyecto.models.Question import Question


class Category(db.Model):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    questions: Mapped[list[Question]] = relationship()

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"
