import pytest
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError

from proyecto.models.Administrator import Administrator
from proyecto.models.Moderator import Moderator
from proyecto.models.RegularUser import RegularUser
from proyecto.models.User import User


def make(cls, email="role@example.com"):
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
    session.expunge_all()

    user = session.scalar(select(User).where(User.email == "role@example.com"))

    assert type(user) is cls
    assert user.role == role


def test_administrator_inherits_from_moderator():
    assert isinstance(make(Administrator), Moderator)


def test_regular_user_is_not_moderator():
    assert not isinstance(make(RegularUser), Moderator)


def test_base_user_cannot_be_instantiated():
    with pytest.raises(InvalidRequestError, match="polymorphic_abstract"):
        make(User)
