from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from proyecto.models.AuthorRecord import AuthorRecord


@runtime_checkable
class Author(Protocol):
    """Anyone who can author an answer: a human user or an AI agent.

    Defined as a Protocol (structural typing) instead of an ABC because
    ABCMeta conflicts with the SQLAlchemy model metaclass. Any class that
    has an author_record and implements get_display_name() satisfies it.
    """

    # Database identity used by Answer to point to its author.
    author_record: AuthorRecord

    def get_display_name(self) -> str: ...
