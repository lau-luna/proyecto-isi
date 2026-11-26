import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from test_answer import create_question
from test_auth import create_test_user

from proyecto.models.HumanAuthorFactory import HumanAuthorFactory
from proyecto.models.Vote import Vote


def users(session):
    asker = create_test_user(session)
    juan = create_test_user(session, username="juan", email="juan@example.com")
    ana = create_test_user(session, username="ana", email="ana@example.com")
    return asker, juan, ana


def test_upvote_adds_a_plus_one_vote(session):
    asker, juan, _ = users(session)
    question = create_question(session, asker)

    question.upvote(juan)
    session.commit()

    vote = session.scalar(select(Vote))
    assert vote.value == 1
    assert vote.voter is juan
    assert vote.date is not None
    assert question.score == 1


def test_downvote_adds_a_minus_one_vote(session):
    asker, juan, _ = users(session)
    question = create_question(session, asker)

    question.downvote(juan)
    session.commit()

    assert session.scalar(select(Vote)).value == -1
    assert question.score == -1


def test_score_is_the_sum_of_the_votes(session):
    asker, juan, ana = users(session)
    question = create_question(session, asker)

    question.upvote(asker)
    question.upvote(juan)
    question.downvote(ana)
    session.commit()

    assert question.score == 1


def test_score_is_zero_without_votes(session):
    asker, _, _ = users(session)

    assert create_question(session, asker).score == 0


def test_voting_the_same_way_again_removes_the_vote(session):
    asker, juan, _ = users(session)
    question = create_question(session, asker)
    question.upvote(juan)
    session.commit()

    question.upvote(juan)
    session.commit()

    assert session.scalars(select(Vote)).all() == []
    assert question.score == 0


def test_voting_the_other_way_changes_the_vote(session):
    asker, juan, _ = users(session)
    question = create_question(session, asker)
    question.upvote(juan)
    session.commit()

    question.downvote(juan)
    session.commit()

    votes = session.scalars(select(Vote)).all()
    assert len(votes) == 1
    assert votes[0].value == -1
    assert question.score == -1


def test_answers_can_be_voted(session):
    asker, juan, _ = users(session)
    answer = create_question(session, asker).add_answer(
        "Press :q", HumanAuthorFactory(asker)
    )
    session.commit()

    answer.upvote(juan)
    session.commit()

    assert answer.score == 1


def test_vote_of_returns_the_user_vote(session):
    asker, juan, ana = users(session)
    question = create_question(session, asker)
    question.downvote(juan)
    session.commit()

    assert question.vote_of(juan) == -1
    assert question.vote_of(ana) is None
    assert question.vote_of(None) is None


def test_database_rejects_two_votes_of_the_same_user_on_a_post(session):
    asker, juan, _ = users(session)
    question = create_question(session, asker)
    session.add_all(
        [
            Vote(post=question, voter=juan, value=1),
            Vote(post=question, voter=juan, value=1),
        ]
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_database_rejects_values_other_than_plus_or_minus_one(session):
    asker, juan, _ = users(session)
    question = create_question(session, asker)
    session.add(Vote(post=question, voter=juan, value=5))

    with pytest.raises(IntegrityError):
        session.commit()
