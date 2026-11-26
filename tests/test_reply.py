from sqlalchemy import select
from test_answer import create_question
from test_answer_routes import login
from test_auth import create_test_user

from proyecto.models.Answer import Answer
from proyecto.models.HumanAuthorFactory import HumanAuthorFactory
from proyecto.models.Reply import Reply


def create_answer(session, question, author):
    answer = question.add_answer("Press :q", HumanAuthorFactory(author))
    session.commit()
    return answer


def test_add_reply_creates_a_reply_with_body_date_and_author(session):
    user = create_test_user(session)
    answer = create_answer(session, create_question(session, user), user)

    reply = answer.add_reply("Thanks!", HumanAuthorFactory(user))
    session.commit()

    saved = session.get(Reply, reply.id)
    assert saved.body == "Thanks!"
    assert saved.published_at is not None
    assert saved.author is user
    assert saved.answer is answer


def test_an_answer_can_have_several_replies_in_order(session):
    user = create_test_user(session)
    other = create_test_user(session, username="juan", email="juan@example.com")
    answer = create_answer(session, create_question(session, user), user)

    answer.add_reply("First", HumanAuthorFactory(other))
    answer.add_reply("Second", HumanAuthorFactory(user))
    session.commit()

    assert [r.body for r in answer.replies] == ["First", "Second"]
    assert [r.author for r in answer.replies] == [other, user]


def test_replies_are_not_answers_of_the_question(session):
    user = create_test_user(session)
    question = create_question(session, user)
    answer = create_answer(session, question, user)

    answer.add_reply("Thanks!", HumanAuthorFactory(user))
    session.commit()

    assert question.answers == [answer]
    assert session.scalars(select(Answer)).all() == [answer]


def test_logged_in_user_can_reply_to_an_answer(client, session):
    user = create_test_user(session)
    question = create_question(session, user)
    answer = create_answer(session, question, user)
    login(client)

    response = client.post(f"/answers/{answer.id}/replies", data={"body": "Thanks!"})

    assert response.status_code == 302
    assert response.headers["Location"] == f"/questions/{question.id}"
    reply = session.scalar(select(Reply))
    assert reply.body == "Thanks!"
    assert reply.answer_id == answer.id
    assert reply.author is user


def test_replying_without_session_redirects_to_login(client, session):
    user = create_test_user(session)
    answer = create_answer(session, create_question(session, user), user)

    response = client.post(f"/answers/{answer.id}/replies", data={"body": "Thanks!"})

    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"
    assert session.scalar(select(Reply)) is None


def test_empty_reply_is_rejected(client, session):
    user = create_test_user(session)
    answer = create_answer(session, create_question(session, user), user)
    login(client)

    response = client.post(f"/answers/{answer.id}/replies", data={"body": "  "})

    assert response.status_code == 400
    assert b"Please write a reply." in response.data
    assert session.scalar(select(Reply)) is None


def test_replying_to_a_missing_answer_returns_404(client, session):
    create_test_user(session)
    login(client)

    response = client.post("/answers/999/replies", data={"body": "Thanks!"})

    assert response.status_code == 404


def test_detail_shows_replies_under_their_answer(client, session):
    user = create_test_user(session)
    question = create_question(session, user)
    answer = create_answer(session, question, user)
    answer.add_reply("Thanks a lot!", HumanAuthorFactory(user))
    session.commit()

    anonymous = client.get(f"/questions/{question.id}")
    login(client)
    logged_in = client.get(f"/questions/{question.id}")

    assert b"Thanks a lot!" in anonymous.data
    assert f'action="/answers/{answer.id}/replies"'.encode() not in anonymous.data
    assert f'action="/answers/{answer.id}/replies"'.encode() in logged_in.data
