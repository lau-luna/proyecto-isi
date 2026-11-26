from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.models.AuthorRecord import AuthorRecord
from proyecto.models.Post import Post

if TYPE_CHECKING:
    from proyecto.models.Answer import Answer
    from proyecto.models.Author import Author


class Reply(Post):
    """A reply to an answer. Replies cannot be replied to (one level only).

    Like Answer, it only knows the Author interface.
    """

    __tablename__ = "reply"

    id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answer.id"), nullable=False)
    answer: Mapped[Answer] = relationship(
        back_populates="replies", foreign_keys=[answer_id]
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), nullable=False)
    author_record: Mapped[AuthorRecord] = relationship()

    __mapper_args__ = {"polymorphic_identity": "reply"}

    def __init__(self, body: str, author: Author) -> None:
        super().__init__(body)
        self.author_record = author.author_record

    @property
    def author(self) -> Author:
        return self.author_record.get_author()
