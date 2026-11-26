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


def test_category_page_shows_only_its_questions(client, session):
    programming, _, _, _ = create_sample_questions(session)

    response = client.get(f"/category/{programming.id}")

    assert response.status_code == 200
    assert b"How do I exit vim" in response.data
    assert b"How do I tune a guitar" not in response.data


def test_tag_page_shows_only_its_questions(client, session):
    _, _, _, guitar_question = create_sample_questions(session)
    guitar_tag = guitar_question.tags[0]

    response = client.get(f"/tag/{guitar_tag.id}")

    assert response.status_code == 200
    assert b"How do I tune a guitar" in response.data
    assert b"How do I exit vim" not in response.data


def test_question_list_links_to_question_detail(client, session):
    _, _, vim_question, _ = create_sample_questions(session)

    response = client.get("/questions")

    assert f"/questions/{vim_question.id}".encode() in response.data
    # The detail link is stretched over the whole card, not only the title.
    assert b"question-card-link" in response.data


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


def test_questions_page_links_to_categories_instead_of_listing_them(client, session):
    create_sample_questions(session)

    response = client.get("/questions")

    assert response.status_code == 200
    assert b'href="/categories"' in response.data
    assert b"Browse categories" in response.data
    assert b'href="/category/' not in response.data.split(b"Latest questions")[0]


def test_search_finds_questions_by_title(client, session):
    create_sample_questions(session)

    response = client.get("/questions?q=VIM")

    assert response.status_code == 200
    assert b"How do I exit vim" in response.data
    assert b"How do I tune a guitar" not in response.data


def test_search_finds_questions_by_body(client, session):
    author = create_test_user(session)
    category = Category("Music")
    session.add(category)
    session.commit()
    create_question(session, author, category, "Strings", body="Nylon or steel?")
    create_question(session, author, category, "Drums", body="Which sticks?")

    response = client.get("/questions?q=nylon")

    assert b"Strings" in response.data
    assert b"Drums" not in response.data


def test_search_without_results_shows_a_message(client, session):
    create_sample_questions(session)

    response = client.get("/questions?q=nonexistent")

    assert response.status_code == 200
    assert b"No questions found" in response.data
    assert b"How do I exit vim" not in response.data


def test_navbar_search_submits_to_questions(client, session):
    response = client.get("/")

    assert b'action="/questions"' in response.data
    assert b'name="q"' in response.data
