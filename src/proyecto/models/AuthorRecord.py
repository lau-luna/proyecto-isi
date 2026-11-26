from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.extensions import db

if TYPE_CHECKING:
    from proyecto.models.Author import Author
    from proyecto.models.User import User


class AuthorRecord(db.Model):
    """Database identity shared by every kind of author.

    An Answer points to this table instead of to a concrete author table
    (user, AI agent, ...). Supporting a new author type only needs a new
    column here and a branch in get_author(); Answer and Question stay
    unchanged.
    """

    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id"), unique=True, nullable=True
    )
    user: Mapped[User | None] = relationship(back_populates="author_record")

    def get_author(self) -> Author:
        """Return the concrete author (a User for now) behind this record."""
        if self.user is not None:
            return self.user
        raise LookupError(f"Author record {self.id} has no author")
