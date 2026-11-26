from test_answer import create_question
from test_answer_routes import login
from test_auth import create_test_user

from proyecto.models.Answer import Answer
from proyecto.models.HumanAuthorFactory import HumanAuthorFactory


def create_answered_question(session):
    asker = create_test_user(session)
    answerer = create_test_user(session, username="juan", email="juan@example.com")
    question = create_question(session, asker)
    answer = question.add_answer("Press :q", HumanAuthorFactory(answerer))
    session.commit()
    return question, answer


def test_question_author_accepts_an_answer(client, session):
    question, answer = create_answered_question(session)
    login(client)  # cata, the question author

    response = client.post(f"/answers/{answer.id}/accept")

    assert response.status_code == 302
    assert response.headers["Location"] == f"/questions/{question.id}"
    assert session.get(Answer, answer.id).accepted is True


def test_other_user_is_rejected_when_accepting(client, session):
    _, answer = create_answered_question(session)
    login(client, email="juan@example.com")

    response = client.post(f"/answers/{answer.id}/accept")

    assert response.status_code == 403
    assert session.get(Answer, answer.id).accepted is False


def test_accepting_without_session_redirects_to_login(client, session):
    _, answer = create_answered_question(session)

    response = client.post(f"/answers/{answer.id}/accept")

    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"
    assert session.get(Answer, answer.id).accepted is False


def test_accepting_a_missing_answer_returns_404(client, session):
    create_test_user(session)
    login(client)

    response = client.post("/answers/999/accept")

    assert response.status_code == 404


def test_accept_button_is_only_shown_to_the_question_author(client, session):
    question, answer = create_answered_question(session)
    action = f'action="/answers/{answer.id}/accept"'.encode()

    anonymous = client.get(f"/questions/{question.id}")
    login(client, email="juan@example.com")
    other_user = client.get(f"/questions/{question.id}")
    client.post("/user/logout")
    login(client)
    author = client.get(f"/questions/{question.id}")

    assert action not in anonymous.data
    assert action not in other_user.data
    assert action in author.data


def test_accepted_answer_is_marked_in_the_detail(client, session):
    question, answer = create_answered_question(session)
    login(client)
    assert b"Accepted answer" not in client.get(f"/questions/{question.id}").data

    client.post(f"/answers/{answer.id}/accept")
    response = client.get(f"/questions/{question.id}")

    assert b"Accepted answer" in response.data
    assert f'action="/answers/{answer.id}/accept"'.encode() not in response.data
