from proyecto.models.User import User


class RegularUser(User):
    """Default role given to every user who registers.

    Stored in the "user" table with role = "regular_user".
    """

    __mapper_args__ = {"polymorphic_identity": "regular_user"}
