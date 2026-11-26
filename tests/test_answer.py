import pytest
from sqlalchemy import select
from test_auth import create_test_user

from proyecto.models.Answer import Answer
from proyecto.models.AuthorFactory import AuthorFactory
from proyecto.models.AuthorRecord import AuthorRecord
from proyecto.models.Category import Category
from proyecto.models.HumanAuthorFactory import HumanAuthorFactory
from proyecto.models.Question import Question


def create_question(session, author):
    category = Category("Programming")
    session.add(category)
    session.commit()
    question = Question(
        title="How do I exit vim",
        category_id=category.id,
        body="Body",
        user_id=author.id,
        tags=[],
    )
    session.add(question)
    session.commit()
    return question


class FakeAuthor:
    """An author type the domain does not know about (e.g. a future bot)."""

    def __init__(self, record):
        self.author_record = record

    def get_display_name(self):
        return "fake"


class FakeAuthorFactory(AuthorFactory):
    def __init__(self, author):
        self.author = author

    def create_author(self):
        return self.author


def test_creating_a_user_creates_its_author_record(session):
    user = create_test_user(session)

    record = session.scalar(select(AuthorRecord).where(AuthorRecord.user_id == user.id))
    assert record is not None
    assert record.get_author() is user


def test_human_author_factory_returns_the_given_user(session):
    user = create_test_user(session)

    assert HumanAuthorFactory(user).create_author() is user


def test_add_answer_creates_an_answer_with_body_date_and_author(session):
    user = create_test_user(session)
    question = create_question(session, user)

    answer = question.add_answer("Press :q", HumanAuthorFactory(user))
    session.commit()

    saved = session.get(Answer, answer.id)
    assert saved.body == "Press :q"
    assert saved.published_at is not None
    assert saved.author is user
    assert saved.question is question


def test_a_question_can_have_several_answers(session):
    user = create_test_user(session)
    other = create_test_user(session, username="juan", email="juan@example.com")
    question = create_question(session, user)

    question.add_answer("Press :q", HumanAuthorFactory(user))
    question.add_answer("Press ZZ", HumanAuthorFactory(other))
    session.commit()

    assert [a.body for a in question.answers] == ["Press :q", "Press ZZ"]
    assert [a.author for a in question.answers] == [user, other]


def test_add_answer_only_needs_an_author_factory(session):
    # A new author type works without changing Question or Answer.
    user = create_test_user(session)
    question = create_question(session, user)
    fake = FakeAuthor(record=user.author_record)

    answer = question.add_answer("Hi", FakeAuthorFactory(fake))

    assert answer.author_record is user.author_record


def test_author_factory_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AuthorFactory()
