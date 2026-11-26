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


def test_answer_is_not_accepted_by_default(session):
    user = create_test_user(session)
    question = create_question(session, user)

    answer = question.add_answer("Press :q", HumanAuthorFactory(user))
    session.commit()

    assert session.get(Answer, answer.id).accepted is False


def test_question_author_can_accept_an_answer(session):
    asker = create_test_user(session)
    answerer = create_test_user(session, username="juan", email="juan@example.com")
    question = create_question(session, asker)
    answer = question.add_answer("Press :q", HumanAuthorFactory(answerer))
    session.commit()

    question.accept_answer(answer, asker)
    session.commit()

    assert session.get(Answer, answer.id).accepted is True


def test_a_question_can_have_several_accepted_answers(session):
    asker = create_test_user(session)
    question = create_question(session, asker)
    first = question.add_answer("Press :q", HumanAuthorFactory(asker))
    second = question.add_answer("Press ZZ", HumanAuthorFactory(asker))
    session.commit()

    question.accept_answer(first, asker)
    question.accept_answer(second, asker)

    assert first.accepted is True
    assert second.accepted is True


def test_other_user_cannot_accept_an_answer(session):
    asker = create_test_user(session)
    other = create_test_user(session, username="juan", email="juan@example.com")
    question = create_question(session, asker)
    answer = question.add_answer("Press :q", HumanAuthorFactory(other))
    session.commit()

    with pytest.raises(PermissionError):
        question.accept_answer(answer, other)

    assert answer.accepted is False


def test_cannot_accept_an_answer_of_another_question(session):
    asker = create_test_user(session)
    question = create_question(session, asker)
    other_question = Question(
        title="Other",
        category_id=question.category_id,
        body="Body",
        user_id=asker.id,
        tags=[],
    )
    session.add(other_question)
    answer = other_question.add_answer("Hi", HumanAuthorFactory(asker))
    session.commit()

    with pytest.raises(ValueError):
        question.accept_answer(answer, asker)

    assert answer.accepted is False
