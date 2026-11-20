from proyecto.models.Moderator import Moderator


class Administrator(Moderator):
    __mapper_args__ = {"polymorphic_identity": "administrator"}
