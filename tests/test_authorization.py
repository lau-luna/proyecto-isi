"""Tests for role-based authorization (issue #5).

The real protected features (publishing, moderating, managing users) belong
to later issues, so this module registers small test-only routes protected
with the same decorators those features will use.
"""

import pytest
from argon2 import PasswordHasher
from sqlalchemy import update

from proyecto import create_app
from proyecto.auth import role_required, user_has_role
from proyecto.models.Administrator import Administrator
from proyecto.models.Moderator import Moderator
from proyecto.models.RegularUser import RegularUser
from proyecto.models.User import User

PASSWORD = "secretpassword"


@pytest.fixture(scope="module")
def app():
    """Testing app with extra routes, one per permission level.

    It overrides the "app" fixture from conftest.py: Flask does not allow
    adding routes after the app has handled its first request, so these
    tests need their own app instance.
    """
    app = create_app("testing")

    @app.route("/test/authenticated")
    @role_required(RegularUser, Moderator)
    def authenticated_only():
        return "authenticated ok"

    @app.route("/test/moderation")
    @role_required(Moderator)
    def moderation_only():
        return "moderation ok"

    @app.route("/test/user-management")
    @role_required(Administrator)
    def administration_only():
        return "administration ok"

    return app


def create_user(session, cls, email):
    user = cls(
        username=email.split("@")[0],
        email=email,
        password_hash=PasswordHasher().hash(PASSWORD),
    )
    session.add(user)
    session.commit()
    return user


def log_in(client, email):
    return client.post("/user/login", data={"email": email, "password": PASSWORD})


@pytest.mark.parametrize(
    "path",
    ["/test/authenticated", "/test/moderation", "/test/user-management"],
)
def test_visitor_is_redirected_to_login(client, init_database, path):
    response = client.get(path)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/login")


@pytest.mark.parametrize(
    ("cls", "path", "expected_status"),
    [
        # Any authenticated user can reach actions such as asking or voting.
        (RegularUser, "/test/authenticated", 200),
        (Moderator, "/test/authenticated", 200),
        (Administrator, "/test/authenticated", 200),
        # Only Moderator and Administrator can delete posts.
        (RegularUser, "/test/moderation", 403),
        (Moderator, "/test/moderation", 200),
        (Administrator, "/test/moderation", 200),
        # Only Administrator can manage users.
        (RegularUser, "/test/user-management", 403),
        (Moderator, "/test/user-management", 403),
        (Administrator, "/test/user-management", 200),
    ],
)
def test_access_depends_on_role(client, session, cls, path, expected_status):
    create_user(session, cls, "member@example.com")
    log_in(client, "member@example.com")

    response = client.get(path)

    assert response.status_code == expected_status


def test_role_change_applies_on_next_request(client, session):
    user = create_user(session, RegularUser, "promoted@example.com")
    log_in(client, "promoted@example.com")
    assert client.get("/test/moderation").status_code == 403

    # Change the role directly in the database; the session cookie still
    # holds only the user id, so the next request must read the new role.
    session.execute(update(User).where(User.id == user.id).values(role="moderator"))
    session.commit()

    assert client.get("/test/moderation").status_code == 200


@pytest.mark.parametrize(
    ("cls", "allowed_roles", "expected"),
    [
        (RegularUser, (Moderator,), False),
        (Moderator, (Moderator,), True),
        (Administrator, (Moderator,), True),
        (Moderator, (Administrator,), False),
    ],
)
def test_user_has_role_follows_class_inheritance(cls, allowed_roles, expected):
    user = cls(username="someone", email="someone@example.com", password_hash="x")

    assert user_has_role(user, *allowed_roles) is expected


def test_user_has_role_is_false_for_visitor():
    assert user_has_role(None, RegularUser, Moderator) is False


@pytest.mark.parametrize(
    ("cls", "visible_badge", "hidden_badges"),
    [
        (RegularUser, None, [b"Moderator", b"Administrator"]),
        (Moderator, b"Moderator", [b"Administrator"]),
        (Administrator, b"Administrator", [b"Moderator"]),
    ],
)
def test_navbar_shows_role_badge(client, session, cls, visible_badge, hidden_badges):
    create_user(session, cls, "badge@example.com")
    log_in(client, "badge@example.com")

    page = client.get("/").data

    if visible_badge is not None:
        assert visible_badge in page
    for badge in hidden_badges:
        assert badge not in page


def test_navbar_shows_no_role_badge_to_visitor(client, init_database):
    page = client.get("/").data

    assert b"Moderator" not in page
    assert b"Administrator" not in page
