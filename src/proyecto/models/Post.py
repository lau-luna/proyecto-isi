from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from proyecto.extensions import db
from proyecto.models.Vote import Vote

if TYPE_CHECKING:
    from proyecto.models.User import User

UPVOTE = 1
DOWNVOTE = -1


class Post(db.Model):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    votes: Mapped[list[Vote]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_on": type,
    }

    def __init__(self, body: str) -> None:
        self.body = body

    @property
    def score(self) -> int:
        """Derived score: the sum of the vote values (+1 / -1)."""
        return sum(vote.value for vote in self.votes)

    def upvote(self, voter: User) -> None:
        self._vote(voter, UPVOTE)

    def downvote(self, voter: User) -> None:
        self._vote(voter, DOWNVOTE)

    def vote_of(self, user: User | None) -> int | None:
        """Return the value of the user's vote on this post, or None."""
        vote = self._find_vote(user)
        return vote.value if vote is not None else None

    def _vote(self, voter: User, value: int) -> None:
        """A user has at most one vote per post.

        Voting the same way again removes the vote; voting the other way
        changes it.
        """
        vote = self._find_vote(voter)
        if vote is None:
            self.votes.append(Vote(voter=voter, value=value))
        elif vote.value == value:
            self.votes.remove(vote)
        else:
            vote.value = value

    def _find_vote(self, user: User | None) -> Vote | None:
        if user is None:
            return None
        for vote in self.votes:
            if vote.user_id == user.id or vote.voter is user:
                return vote
        return None
