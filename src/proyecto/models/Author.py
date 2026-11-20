from typing import Protocol, runtime_checkable


@runtime_checkable
class Author(Protocol):
    """Anyone who can author an answer: a human user or an AI agent.

    Defined as a Protocol (structural typing) instead of an ABC because
    ABCMeta conflicts with the SQLAlchemy model metaclass. Any class that
    implements get_display_name() satisfies this interface.
    """

    def get_display_name(self) -> str: ...
