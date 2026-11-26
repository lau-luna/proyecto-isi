from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.models.AuthorRecord import AuthorRecord
from proyecto.models.Post import Post

if TYPE_CHECKING:
    from proyecto.models.Author import Author
    from proyecto.models.Question import Question


class Answer(Post):
    """An answer to a question. It only knows the Author interface."""

    __tablename__ = "answer"

    id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=False)
    question: Mapped[Question] = relationship(
        back_populates="answers", foreign_keys=[question_id]
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), nullable=False)
    author_record: Mapped[AuthorRecord] = relationship()

    __mapper_args__ = {"polymorphic_identity": "answer"}

    def __init__(self, body: str, author: Author) -> None:
        super().__init__(body)
        self.author_record = author.author_record

    @property
    def author(self) -> Author:
        return self.author_record.get_author()
