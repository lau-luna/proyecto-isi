from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.models.Post import Post
from proyecto.models.QuestionTag import question_tag
from proyecto.models.Tag import Tag

class Question(Post):
    __tablename__ = "question"
    id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    tags: Mapped[list[Tag]] = relationship(secondary=question_tag)

    __mapper_args__ = {"polymorphic_identity": "question"}

    def __init__(self, title: str, category_id: int, body: str, user_id: int, tags: list[Tag]) -> None:
        super().__init__(body)
        self.category_id = category_id
        self.title = title
        self.user_id = user_id
        self.tags = tags
