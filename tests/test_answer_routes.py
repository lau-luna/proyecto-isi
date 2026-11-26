from sqlalchemy import select
from test_answer import create_question
from test_auth import create_test_user

from proyecto.models.Answer import Answer


def login(client, email="cata@example.com", password="secretpassword"):
    client.post("/user/login", data={"email": email, "password": password})


def test_logged_in_user_can_answer_a_question(client, session):
    user = create_test_user(session)
    question = create_question(session, user)
    login(client)

    response = client.post(
        f"/questions/{question.id}/answers", data={"body": "Press :q"}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == f"/questions/{question.id}"
    answer = session.scalar(select(Answer))
    assert answer.body == "Press :q"
    assert answer.question_id == question.id
    assert answer.published_at is not None


def test_answer_author_is_the_logged_in_user(client, session):
    asker = create_test_user(session)
    answerer = create_test_user(session, username="juan", email="juan@example.com")
    question = create_question(session, asker)
    login(client, email="juan@example.com")

    client.post(f"/questions/{question.id}/answers", data={"body": "Press :q"})

    assert session.scalar(select(Answer)).author is answerer


def test_a_question_can_receive_several_answers(client, session):
    user = create_test_user(session)
    question = create_question(session, user)
    login(client)

    client.post(f"/questions/{question.id}/answers", data={"body": "Press :q"})
    client.post(f"/questions/{question.id}/answers", data={"body": "Press ZZ"})

    bodies = session.scalars(select(Answer.body).order_by(Answer.id)).all()
    assert bodies == ["Press :q", "Press ZZ"]


def test_answering_without_session_redirects_to_login(client, session):
    user = create_test_user(session)
    question = create_question(session, user)

    response = client.post(
        f"/questions/{question.id}/answers", data={"body": "Press :q"}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"
    assert session.scalar(select(Answer)) is None


def test_empty_answer_is_rejected(client, session):
    user = create_test_user(session)
    question = create_question(session, user)
    login(client)

    response = client.post(f"/questions/{question.id}/answers", data={"body": "  "})

    assert response.status_code == 400
    assert b"Please write an answer." in response.data
    assert session.scalar(select(Answer)) is None


def test_answering_a_missing_question_returns_404(client, session):
    create_test_user(session)
    login(client)

    response = client.post("/questions/999/answers", data={"body": "Press :q"})

    assert response.status_code == 404


def test_detail_lists_answers_with_body_author_and_date(client, session):
    asker = create_test_user(session)
    create_test_user(session, username="juan", email="juan@example.com")
    question = create_question(session, asker)
    login(client, email="juan@example.com")
    client.post(f"/questions/{question.id}/answers", data={"body": "Press :q"})
    answer = session.scalar(select(Answer))

    response = client.get(f"/questions/{question.id}")

    assert b"Press :q" in response.data
    assert b"juan" in response.data
    assert answer.published_at.strftime("%Y-%m-%d").encode() in response.data
    assert b"No answers yet." not in response.data


def test_detail_shows_answer_form_only_when_logged_in(client, session):
    user = create_test_user(session)
    question = create_question(session, user)

    anonymous = client.get(f"/questions/{question.id}")
    login(client)
    logged_in = client.get(f"/questions/{question.id}")

    # The body textarea is created by the OverType editor in the browser.
    assert b'id="answer-editor"' not in anonymous.data
    assert b"Log in to answer" in anonymous.data
    assert b'id="answer-editor"' in logged_in.data
    assert b'textareaProps: { name: "body" }' in logged_in.data
    assert f'action="/questions/{question.id}/answers"'.encode() in logged_in.data
