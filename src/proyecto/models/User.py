from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.extensions import db
from proyecto.models.Question import Question

pass_hasher = PasswordHasher()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="regular_user"
    )
    questions: Mapped[list[Question]] = relationship()

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "user",
    }

    def __init__(self, username: str, email: str, password_hash: str) -> None:
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def get_display_name(self) -> str:
        return self.username

    def verify_password(self, password: str) -> bool:
        try:
            return pass_hasher.verify(self.password_hash, password)
        except VerifyMismatchError, InvalidHashError:
            return False

    def post_question(self, title, body, category, question, tags):
        # TODO: implement
        pass
