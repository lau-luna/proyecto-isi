import pytest
from argon2 import PasswordHasher
from sqlalchemy import select

from proyecto.models.RegularUser import RegularUser
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
    assert isinstance(user, RegularUser)
    assert user.role == "regular_user"
    assert user.username == user_data["username"]


def test_duplicate_email_is_rejected(client, session, user_data):
    client.post("/user/register", data=user_data)
    response = client.post("/user/register", data=user_data)

    assert response.status_code == 400
    assert b"Email already exists" in response.data
    assert len(session.scalars(select(User)).all()) == 1


def test_missing_data_is_rejected(client, session, user_data):
    user_data.update(
        {"username": "", "email": "", "password": "", "password_confirm": ""}
    )
    response = client.post("/user/register", data=user_data)

    assert response.status_code == 400
    assert b"required" in response.data.lower()
    assert b"is-danger" in response.data
    assert session.scalars(select(User)).all() == []


def test_missing_form_key_is_rejected(client, session, user_data):
    del user_data["password_confirm"]
    response = client.post("/user/register", data=user_data)

    assert response.status_code == 400
    assert b"This field is required" in response.data
    assert session.scalars(select(User)).all() == []


def test_invalid_email_is_rejected(client, session, user_data):
    user_data["email"] = "not-an-email"
    response = client.post("/user/register", data=user_data)

    assert response.status_code == 400
    assert b"Enter a valid email address" in response.data
    assert session.scalars(select(User)).all() == []


def test_password_mismatch_returns_400(client, session, user_data):
    user_data["password_confirm"] = "different-password"
    response = client.post("/user/register", data=user_data)

    assert response.status_code == 400
    assert b"Passwords do not match" in response.data
    assert session.scalars(select(User)).all() == []


def test_password_is_stored_as_hash(client, session, user_data):
    client.post("/user/register", data=user_data)

    user = session.scalar(select(User).where(User.email == user_data["email"]))
    assert user is not None
    assert user.password_hash != user_data["password"]
    assert user.password_hash.startswith("$argon2id$")
    assert PasswordHasher().verify(user.password_hash, user_data["password"])


def test_password_with_special_chars_is_not_modified(client, session, user_data):
    user_data["password"] = "a&b\"<c>d'e"
    user_data["password_confirm"] = user_data["password"]
    client.post("/user/register", data=user_data)

    user = session.scalar(select(User).where(User.email == user_data["email"]))
    assert user is not None
    assert PasswordHasher().verify(user.password_hash, user_data["password"])

def test_register_without_csrf_token_is_rejected(app, client, monkeypatch, user_data):
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", True)

    response = client.post(
        "/user/register",
        data=user_data
    )

    assert response.status_code == 400
    assert b"The CSRF token is missing." in response.data
