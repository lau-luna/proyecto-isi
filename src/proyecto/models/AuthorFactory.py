from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from proyecto.models.Author import Author


class AuthorFactory(ABC):
    """Factory Method: decides who authors a new answer.

    Question.add_answer() only knows this abstract class, so it never depends
    on whether the author is a human user or an AI agent.
    """

    @abstractmethod
    def create_author(self) -> Author: ...
