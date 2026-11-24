from proyecto.models.User import User


class Moderator(User):
    """User who can moderate content (e.g. delete posts).

    Stored in the "user" table with role = "moderator".
    """

    __mapper_args__ = {"polymorphic_identity": "moderator"}
