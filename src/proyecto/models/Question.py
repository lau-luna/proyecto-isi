from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.extensions import db
from proyecto.models.Post import Post
from proyecto.models.QuestionTag import question_tag
from proyecto.models.Tag import Tag

if TYPE_CHECKING:
    from proyecto.models.Category import Category
    from proyecto.models.User import User


class Question(Post):
    __tablename__ = "question"
    id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    tags: Mapped[list[Tag]] = relationship(secondary=question_tag)
    author: Mapped[User] = relationship(back_populates="questions")
    category: Mapped[Category] = relationship(back_populates="questions")

    __mapper_args__ = {"polymorphic_identity": "question"}

    def __init__(
        self, title: str, category_id: int, body: str, user_id: int, tags: list[Tag]
    ) -> None:
        super().__init__(body)
        self.category_id = category_id
        self.title = title
        self.user_id = user_id
        self.tags = tags

    @staticmethod
    def find_all(
        category_id: int | None = None, tag_name: str | None = None
    ) -> list[Question]:
        """Return questions, newest first, optionally filtered by category or tag."""
        query = select(Question).order_by(
            Question.published_at.desc(), Question.id.desc()
        )

        if category_id is not None:
            query = query.where(Question.category_id == category_id)

        if tag_name:
            query = query.where(Question.tags.any(Tag.name == tag_name.strip().lower()))

        return list(db.session.scalars(query).all())
