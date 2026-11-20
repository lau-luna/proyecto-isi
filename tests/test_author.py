from proyecto.models.Author import Author
from proyecto.models.User import User


def make_user():
    return User(username="testuser", email="test@example.com", password_hash="hash")


def test_user_implements_author():
    assert isinstance(make_user(), Author)


def test_user_display_name_is_username():
    assert make_user().get_display_name() == "testuser"
