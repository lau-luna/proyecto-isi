from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from proyecto.models.Post import Post


class Question(Post):
    __tablename__ = "question"
    id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "question"}
