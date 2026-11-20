from proyecto.models.User import User


class RegularUser(User):
    __mapper_args__ = {"polymorphic_identity": "regular_user"}
