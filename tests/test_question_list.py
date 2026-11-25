from test_auth import create_test_user

from proyecto.models.Category import Category
from proyecto.models.Question import Question
from proyecto.models.Tag import Tag


def create_question(session, author, category, title, tag_names=(), body="Body"):
    tags = [Tag(name) for name in tag_names]
    question = Question(
        title=title,
        category_id=category.id,
        body=body,
        user_id=author.id,
        tags=tags,
    )
    session.add(question)
    session.commit()
    return question


def create_sample_questions(session):
    author = create_test_user(session)
    programming = Category("Programming")
    music = Category("Music")
    session.add_all([programming, music])
    session.commit()

    vim_question = create_question(
        session, author, programming, "How do I exit vim", ["vim"]
    )
    guitar_question = create_question(
        session, author, music, "How do I tune a guitar", ["guitar"]
    )
    return programming, music, vim_question, guitar_question


def test_question_list_is_public(client, session):
    create_sample_questions(session)

    response = client.get("/questions")

    assert response.status_code == 200
    assert b"How do I exit vim" in response.data
    assert b"How do I tune a guitar" in response.data


def test_question_list_shows_title_author_category_tags_and_date(client, session):
    _, _, vim_question, _ = create_sample_questions(session)

    response = client.get("/questions")

    assert b"How do I exit vim" in response.data
    assert b"cata" in response.data
    assert b"Programming" in response.data
    assert b"vim" in response.data
    published = vim_question.published_at.strftime("%Y-%m-%d")
    assert published.encode() in response.data


def test_question_list_filters_by_category(client, session):
    programming, _, _, _ = create_sample_questions(session)

    response = client.get(f"/questions?category={programming.id}")

    assert response.status_code == 200
    assert b"How do I exit vim" in response.data
    assert b"How do I tune a guitar" not in response.data


def test_question_list_filters_by_tag(client, session):
    create_sample_questions(session)

    response = client.get("/questions?tag=guitar")

    assert response.status_code == 200
    assert b"How do I tune a guitar" in response.data
    assert b"How do I exit vim" not in response.data


def test_question_list_shows_message_when_there_are_no_results(client, session):
    create_sample_questions(session)

    response = client.get("/questions?tag=nonexistent")

    assert response.status_code == 200
    assert b"No questions found." in response.data
    assert b"How do I exit vim" not in response.data


def test_question_detail_shows_the_full_question(client, session):
    _, _, vim_question, _ = create_sample_questions(session)

    response = client.get(f"/questions/{vim_question.id}")

    assert response.status_code == 200
    assert b"How do I exit vim" in response.data
    assert b"Body" in response.data
    assert b"cata" in response.data
    assert b"Programming" in response.data
    assert b"vim" in response.data
    assert b"Answers" in response.data


def test_question_detail_returns_404_for_missing_question(client, session):
    response = client.get("/questions/999")

    assert response.status_code == 404
