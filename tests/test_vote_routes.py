import pytest
from sqlalchemy import select
from test_answer import create_question
from test_answer_routes import login
from test_auth import create_test_user

from proyecto.models.HumanAuthorFactory import HumanAuthorFactory
from proyecto.models.Vote import Vote


def setup_question(session):
    asker = create_test_user(session)
    create_test_user(session, username="juan", email="juan@example.com")
    return create_question(session, asker)


def test_logged_in_user_upvotes_a_question(client, session):
    question = setup_question(session)
    login(client, email="juan@example.com")

    response = client.post(
        f"/posts/{question.id}/upvote", data={"next": f"/questions/{question.id}"}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == f"/questions/{question.id}"
    assert session.scalar(select(Vote)).value == 1


def test_logged_in_user_downvotes_an_answer(client, session):
    question = setup_question(session)
    answer = question.add_answer("Press :q", HumanAuthorFactory(question.author))
    session.commit()
    login(client, email="juan@example.com")

    client.post(f"/posts/{answer.id}/downvote")

    vote = session.scalar(select(Vote))
    assert vote.value == -1
    assert vote.post_id == answer.id


def test_pressing_the_same_button_twice_removes_the_vote(client, session):
    question = setup_question(session)
    login(client, email="juan@example.com")

    client.post(f"/posts/{question.id}/upvote")
    client.post(f"/posts/{question.id}/upvote")

    assert session.scalars(select(Vote)).all() == []


def test_pressing_the_other_button_changes_the_vote(client, session):
    question = setup_question(session)
    login(client, email="juan@example.com")

    client.post(f"/posts/{question.id}/upvote")
    client.post(f"/posts/{question.id}/downvote")

    votes = session.scalars(select(Vote)).all()
    assert [v.value for v in votes] == [-1]


def test_visitor_without_session_cannot_vote(client, session):
    question = setup_question(session)

    response = client.post(f"/posts/{question.id}/upvote")

    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"
    assert session.scalar(select(Vote)) is None


def test_voting_a_missing_post_returns_404(client, session):
    setup_question(session)
    login(client)

    assert client.post("/posts/999/upvote").status_code == 404


def test_replies_cannot_be_voted(client, session):
    question = setup_question(session)
    answer = question.add_answer("Press :q", HumanAuthorFactory(question.author))
    reply = answer.add_reply("Thanks", HumanAuthorFactory(question.author))
    session.commit()
    login(client)

    assert client.post(f"/posts/{reply.id}/upvote").status_code == 404
    assert session.scalar(select(Vote)) is None


def test_external_next_url_is_ignored(client, session):
    question = setup_question(session)
    login(client)

    response = client.post(
        f"/posts/{question.id}/upvote", data={"next": "https://evil.example.com"}
    )

    assert response.headers["Location"] == f"/questions/{question.id}"


def test_score_is_shown_on_the_detail_and_the_list(client, session):
    question = setup_question(session)
    answer = question.add_answer("Press :q", HumanAuthorFactory(question.author))
    session.commit()
    login(client, email="juan@example.com")
    client.post(f"/posts/{question.id}/downvote")
    client.post(f"/posts/{answer.id}/upvote")

    detail = client.get(f"/questions/{question.id}").data
    listing = client.get("/questions").data

    assert f'data-score-for="{question.id}">-1<'.encode() in detail
    assert f'data-score-for="{answer.id}">1<'.encode() in detail
    assert f'data-score-for="{question.id}">-1<'.encode() in listing


def test_vote_buttons_post_to_the_vote_routes(client, session):
    question = setup_question(session)

    response = client.get(f"/questions/{question.id}")

    assert f'action="/posts/{question.id}/upvote"'.encode() in response.data
    assert f'action="/posts/{question.id}/downvote"'.encode() in response.data


def test_the_user_vote_is_highlighted_and_next_points_to_the_page(client, session):
    question = setup_question(session)
    login(client, email="juan@example.com")
    client.post(f"/posts/{question.id}/upvote")

    detail = client.get(f"/questions/{question.id}").data
    listing = client.get("/questions").data

    assert b'is-primary"\n      aria-label="Upvote"' in detail
    assert f'name="next" value="/questions/{question.id}?"'.encode() in detail
    assert b'is-primary"\n      aria-label="Upvote"' in listing


@pytest.mark.parametrize(
    "next_url",
    [
        "https://evil.example.com",
        "//evil.example.com",
        "/\t/evil.example.com",
        "/\\evil.example.com",
        "\\\\evil.example.com",
        "/questions\n/x",
    ],
)
def test_next_urls_that_could_leave_the_site_are_ignored(client, session, next_url):
    question = setup_question(session)
    login(client)

    response = client.post(f"/posts/{question.id}/upvote", data={"next": next_url})

    assert response.headers["Location"] == f"/questions/{question.id}"


def test_a_concurrent_duplicate_vote_does_not_crash(client, session, monkeypatch):
    # Simulates two requests of the same user racing: the second one does not
    # see the first vote and the database unique constraint rejects it.
    from proyecto.models.Post import Post

    question = setup_question(session)
    login(client, email="juan@example.com")
    client.post(f"/posts/{question.id}/upvote")
    monkeypatch.setattr(Post, "_find_vote", lambda self, user: None)

    response = client.post(f"/posts/{question.id}/upvote")

    assert response.status_code == 302
    assert len(session.scalars(select(Vote)).all()) == 1
