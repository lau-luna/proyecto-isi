"""Tests for user roles (issue #5).

Covers the role classes (RegularUser, Moderator, Administrator), their
inheritance, and the CHECK constraint on the "role" column.
"""

import pytest
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from proyecto.models.Administrator import Administrator
from proyecto.models.Moderator import Moderator
from proyecto.models.RegularUser import RegularUser
from proyecto.models.User import User


def make(cls, email="role@example.com"):
    """Build (without saving) a user of the given role class."""
    return cls(username="roleuser", email=email, password_hash="hash")


@pytest.mark.parametrize(
    ("cls", "role"),
    [
        (RegularUser, "regular_user"),
        (Moderator, "moderator"),
        (Administrator, "administrator"),
    ],
)
def test_user_subtype_is_persisted_with_its_role(session, cls, role):
    session.add(make(cls))
    session.commit()
    # Forget the objects in memory, so the next query really reads the row
    # back from the database instead of returning the same Python object.
    session.expunge_all()

    user = session.scalar(select(User).where(User.email == "role@example.com"))

    # "type(...) is" (not isinstance) checks the exact class: an
    # Administrator must not come back as a plain Moderator.
    assert type(user) is cls
    assert user.role == role


def test_administrator_inherits_from_moderator():
    assert isinstance(make(Administrator), Moderator)


def test_regular_user_is_not_moderator():
    assert not isinstance(make(RegularUser), Moderator)


def test_base_user_cannot_be_instantiated():
    with pytest.raises(InvalidRequestError, match="polymorphic_abstract"):
        make(User)


def insert_user_with_role(session, role, email="role@example.com"):
    # Insert straight into the table, skipping the ORM classes,
    # so we can try role values that no class would ever write.
    session.execute(
        insert(User.__table__).values(
            username="roleuser", email=email, password_hash="hash", role=role
        )
    )


def test_database_rejects_an_unknown_role(session):
    with pytest.raises(IntegrityError):
        insert_user_with_role(session, "hacker")


def test_database_accepts_every_role_defined_by_a_class(session):
    # SQLAlchemy keeps a map {role value: class} with one entry per subclass.
    # If someone adds a new role class but forgets the CHECK, this test fails.
    roles_defined_by_classes = User.__mapper__.polymorphic_map.keys()

    for number, role in enumerate(roles_defined_by_classes):
        insert_user_with_role(session, role, email=f"user{number}@example.com")

    saved_roles = set(session.scalars(select(User.role)))
    assert saved_roles == set(roles_defined_by_classes)
