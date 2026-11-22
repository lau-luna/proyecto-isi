from sqlalchemy import DateTime, String, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

def Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(String(), nullable=False)
    published_at: Column(DateTime(timezone=True), server_default=func.now()) 
    score: Mapped[int] = mapped_column(Integer, server_default=0)
    
    # TODO: implement
    def upvote(User):
        return None
    
    # TODO: implement
    def downvote(User):
        return None


