from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from proyecto.extensions import db


class Post(db.Model):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(String(), nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    score: Mapped[int] = mapped_column(server_default="0", nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)

    __mapped_args__ = {
        "polymorphic_on": type,
    }

    # TODO: implement
    def upvote(self, User):
        pass

    # TODO: implement
    def downvote(self, User):
        pass
