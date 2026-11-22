from proyecto.models.Moderator import Moderator


class Administrator(Moderator):
    """User who can manage other users.

    Inherits from Moderator, so an Administrator also has every Moderator
    permission: isinstance(administrator, Moderator) is True.
    Stored in the "user" table with role = "administrator".
    """

    __mapper_args__ = {"polymorphic_identity": "administrator"}
