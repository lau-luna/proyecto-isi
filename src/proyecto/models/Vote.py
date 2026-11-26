from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from proyecto.extensions import db

if TYPE_CHECKING:
    from proyecto.models.Post import Post
    from proyecto.models.User import User


class Vote(db.Model):
    """A +1 or -1 vote of a user on a post (question or answer)."""

    __tablename__ = "vote"
    __table_args__ = (
        # A user can have only one vote per post.
        UniqueConstraint("post_id", "user_id", name="uq_vote_post_user"),
        CheckConstraint("value IN (1, -1)", name="ck_vote_value"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    post: Mapped[Post] = relationship(back_populates="votes")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    voter: Mapped[User] = relationship()
    value: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
