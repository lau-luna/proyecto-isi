from proyecto.models.Author import Author
from proyecto.models.RegularUser import RegularUser


def make_user():
    return RegularUser(
        username="testuser", email="test@example.com", password_hash="hash"
    )


def test_user_implements_author():
    assert isinstance(make_user(), Author)


def test_user_display_name_is_username():
    assert make_user().get_display_name() == "testuser"
