import pytest
from argon2 import PasswordHasher

from proyecto import create_app
from proyecto.config import ProductionConfig
from proyecto.models.RegularUser import RegularUser

pass_hasher = PasswordHasher()


def create_test_user(
    session,
    username="cata",
    email="cata@example.com",
    password="secretpassword",
):
    user = RegularUser(
        username=username,
        email=email,
        password_hash=pass_hasher.hash(password),
    )
    session.add(user)
    session.commit()
    return user


def test_verify_password(session):
    user = create_test_user(session, password="correct-password")

    assert user.verify_password("correct-password") is True
    assert user.verify_password("wrong-password") is False

    user.password_hash = "invalid-hash-format"
    assert user.verify_password("correct-password") is False


def test_login_page_renders(client):
    response = client.get("/user/login")

    assert response.status_code == 200
    assert b"Log in" in response.data


def test_login_without_csrf_token_is_rejected(app, client, monkeypatch):
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", True)

    response = client.post(
        "/user/login",
        data={"email": "cata@example.com", "password": "secretpassword"},
    )

    assert response.status_code == 400
    assert b"The CSRF token is missing." in response.data
    with client.session_transaction() as flask_session:
        assert "user_id" not in flask_session


def test_login_success_cookie_and_session_persistence(client, session):
    user = create_test_user(session)
    user_id = user.id

    response = client.post(
        "/user/login",
        data={"email": "cata@example.com", "password": "secretpassword"},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # Verifica atributos de seguridad de la cookie
    cookies = response.headers.getlist("Set-Cookie")
    session_cookie = next(c for c in cookies if c.startswith("session="))
    assert "HttpOnly" in session_cookie
    assert "SameSite=Lax" in session_cookie

    # Verifica que la sesion guarde solo user_id (sin rol ni password)
    with client.session_transaction() as flask_session:
        assert dict(flask_session) == {"user_id": user_id}

    # Verifica que la sesion persista en pedidos siguientes (g.user)
    home_response = client.get("/")
    assert home_response.status_code == 200
    assert b"cata" in home_response.data
    assert b"Log Out" in home_response.data


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("cata@example.com", "wrong-password"),
        ("noexiste@example.com", "secretpassword"),
    ],
)
def test_login_invalid_credentials_generic_error(client, session, email, password):
    create_test_user(session)

    response = client.post(
        "/user/login",
        data={"email": email, "password": password},
    )

    assert response.status_code == 401
    assert b"Invalid email or password" in response.data

    with client.session_transaction() as flask_session:
        assert "user_id" not in flask_session


def test_logout_clears_session(client, session):
    create_test_user(session)

    client.post(
        "/user/login",
        data={"email": "cata@example.com", "password": "secretpassword"},
    )

    logout_response = client.post("/user/logout")
    assert logout_response.status_code == 302
    assert logout_response.headers["Location"] == "/"

    with client.session_transaction() as flask_session:
        assert "user_id" not in flask_session

    home_response = client.get("/")
    assert b"Log in" in home_response.data
    assert b"Log Out" not in home_response.data


def test_login_required_redirects_anonymous_user(client):
    response = client.post("/user/logout")

    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"


def test_production_config_requires_secret_key_and_secure_cookie(monkeypatch):
    monkeypatch.setattr(
        ProductionConfig, "SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:"
    )
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", None)
    with pytest.raises(RuntimeError, match="SECRET_KEY must be set in production"):
        create_app("production")

    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "super-secret-prod-key")
    prod_app = create_app("production")
    assert prod_app.config["SESSION_COOKIE_SECURE"] is True
