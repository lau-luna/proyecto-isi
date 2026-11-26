from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.models.Answer import Answer
from proyecto.models.Post import Post
from proyecto.models.QuestionTag import question_tag
from proyecto.models.Tag import Tag

if TYPE_CHECKING:
    from proyecto.models.AuthorFactory import AuthorFactory
    from proyecto.models.Category import Category
    from proyecto.models.User import User


class Question(Post):
    __tablename__ = "question"
    id: Mapped[int] = mapped_column(ForeignKey("post.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped[Category] = relationship(back_populates="questions")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    tags: Mapped[list[Tag]] = relationship(secondary=question_tag)
    author: Mapped[User] = relationship(back_populates="questions")
    answers: Mapped[list[Answer]] = relationship(
        back_populates="question",
        foreign_keys="Answer.question_id",
        order_by="Answer.id",
    )

    __mapper_args__ = {"polymorphic_identity": "question"}

    def __init__(
        self, title: str, category_id: int, body: str, user_id: int, tags: list[Tag]
    ) -> None:
        super().__init__(body)
        self.category_id = category_id
        self.title = title
        self.user_id = user_id
        self.tags = tags

    def add_answer(self, body: str, factory: AuthorFactory) -> Answer:
        """Create an answer whose author is chosen by the given factory.

        The question does not know if the author is a human or an AI agent.
        """
        author = factory.create_author()
        answer = Answer(body=body, author=author)
        self.answers.append(answer)
        return answer

    def accept_answer(self, answer: Answer, requester: User) -> None:
        """Mark an answer as accepted. Only the question author can do it.

        A question can have several accepted answers.
        """
        self._check_can_change_acceptance(answer, requester)
        answer.mark_as_accepted()

    def unaccept_answer(self, answer: Answer, requester: User) -> None:
        """Remove the acceptance of an answer, with the same rules as accepting."""
        self._check_can_change_acceptance(answer, requester)
        answer.unmark_as_accepted()

    def _check_can_change_acceptance(self, answer: Answer, requester: User) -> None:
        if answer.question is not self:
            raise ValueError("The answer does not belong to this question")
        if requester.id != self.user_id:
            raise PermissionError("Only the question author can accept answers")
