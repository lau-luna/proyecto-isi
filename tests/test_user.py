import pytest
from argon2 import PasswordHasher
from sqlalchemy import select

from proyecto.models.User import User


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "secure-password",
        "password_confirm": "secure-password",
    }


def test_valid_registration(client, session, user_data):
    response = client.post("/user/register", data=user_data)

    assert response.status_code == 200
    user = session.scalar(select(User).where(User.email == user_data["email"]))
    assert user is not None
    assert user.username == user_data["username"]


def test_duplicate_email_is_rejected(client, session, user_data):
    client.post("/user/register", data=user_data)
    response = client.post("/user/register", data=user_data)

    assert response.status_code == 200
    assert b"Email already exists" in response.data
    assert len(session.scalars(select(User)).all()) == 1


def test_missing_data_is_rejected(client, session, user_data):
    user_data.update(
        {"username": "", "email": "", "password": "", "password_confirm": ""}
    )
    response = client.post("/user/register", data=user_data)

    assert response.status_code == 200
    assert b"required" in response.data.lower()
    assert b"is-danger" in response.data
    assert session.scalars(select(User)).all() == []


def test_password_is_stored_as_hash(client, session, user_data):
    client.post("/user/register", data=user_data)

    user = session.scalar(select(User).where(User.email == user_data["email"]))
    assert user is not None
    assert user.password_hash != user_data["password"]
    assert user.password_hash.startswith("$argon2id$")
    assert PasswordHasher().verify(user.password_hash, user_data["password"])
