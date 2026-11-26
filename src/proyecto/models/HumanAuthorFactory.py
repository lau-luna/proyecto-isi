from typing import TYPE_CHECKING

from proyecto.models.AuthorFactory import AuthorFactory

if TYPE_CHECKING:
    from proyecto.models.User import User


class HumanAuthorFactory(AuthorFactory):
    """Gives the user who is answering (the authenticated user)."""

    def __init__(self, user: User) -> None:
        self.user = user

    def create_author(self) -> User:
        return self.user
