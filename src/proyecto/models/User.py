from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from proyecto.extensions import db
from proyecto.models.Question import Question

pass_hasher = PasswordHasher()


class User(db.Model):
    """Base class for every person registered on the platform.

    Roles are modelled with single-table inheritance: RegularUser, Moderator
    and Administrator are subclasses of User, and all of them are stored in
    this same "user" table. The "role" column says which subclass each row is.
    """

    __tablename__ = "user"
    __table_args__ = (
        # CHECK constraint: the database itself rejects any role that is not
        # one of these three, even if the row is written outside the ORM.
        # If you add a new role subclass, add its value here too and create a
        # new migration (see test_database_accepts_every_role_defined_by_a_class).
        CheckConstraint(
            "role IN ('regular_user', 'moderator', 'administrator')",
            name="ck_user_role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    # Discriminator column: SQLAlchemy fills it with the subclass identity
    # ("regular_user", "moderator" or "administrator") when saving a user.
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="regular_user"
    )
    questions: Mapped[list[Question]] = relationship()

    __mapper_args__ = {
        # When loading a row, SQLAlchemy reads "role" to decide which
        # subclass to build (e.g. "moderator" -> Moderator).
        "polymorphic_on": role,
        # User is abstract (as in the class diagram): User(...) raises an
        # error, so every user must be created as one of its subclasses.
        "polymorphic_abstract": True,
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
