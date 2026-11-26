import pytest
from sqlalchemy import select
from test_auth import create_test_user

from proyecto.extensions import db
from proyecto.models.Category import Category
from proyecto.models.Post import Post
from proyecto.models.Question import Question
from proyecto.models.Tag import Tag
from proyecto.models.User import User


@pytest.fixture
def user_data():
    return {"email": "cata@example.com", "password": "secretpassword"}


def login_test_user(client, session):
    create_test_user(session)
    client.post(
        "/user/login", data={"email": "cata@example.com", "password": "secretpassword"}
    )


def test_question_form_requires_login(client):
    response = client.get("/question")

    assert response.status_code == 302
    assert response.headers["Location"] == "/user/login"


def test_question_form_renders(client, session):
    login_test_user(client, session)

    response = client.get("/question")

    assert response.status_code == 200
    assert b"Create post" in response.data
    assert b'name="title"' in response.data
    assert b'name="category"' in response.data
    assert b'name="body"' in response.data
    assert b'name="tags"' in response.data
    assert b'value="Post"' in response.data
    assert b"Log Out" in response.data


def test_posting_a_question_requires_category(client, session):
    login_test_user(client, session)
    response = client.post(
        "/question",
        data={
            "title": "Example title",
            "category": "",
            "body": "Example Body",
            "tags": "",
        },
    )
    assert response.status_code == 400
    assert b"Please select a category." in response.data
    assert session.scalars(select(Question)).all() == []


def test_posting_a_question_requires_title(client, session):
    login_test_user(client, session)
    category = Category("Programming")
    session.add(category)
    session.commit()

    response = client.post(
        "/question",
        data={
            "title": "",
            "category": str(category.id),
            "body": "Example Body",
            "tags": "",
        },
    )
    assert response.status_code == 400
    assert b"Please enter a valid title." in response.data
    assert session.scalars(select(Question)).all() == []


def test_posting_a_question_requires_body(client, session):
    login_test_user(client, session)
    category = Category("Programming")
    session.add(category)
    session.commit()

    response = client.post(
        "/question",
        data={
            "title": "",
            "category": str(category.id),
            "body": "",
            "tags": "",
        },
    )
    assert response.status_code == 400
    assert b"Please enter a valid body." in response.data
    assert session.scalars(select(Question)).all() == []


def test_posting_a_valid_question_is_created_and_stored(client, session):
    login_test_user(client, session)
    category = Category("Programming")
    session.add(category)
    session.commit()

    response = client.post(
        "/question",
        data={
            "title": "How do I exit vim",
            "category": str(category.id),
            "body": "pls help I can't exit",
            "tags": "vim code-editors",
        },
    )

    assert response.status_code == 302

    questions = db.session.scalars(select(Question).join(Category)).all()
    assert len(questions) == 1
    question = questions[0]
    assert question.title == "How do I exit vim"
    assert question.body == "pls help I can't exit"

    category = db.session.scalar(select(Category).where(Category.name == "Programming"))
    assert category is not None
    assert question.category_id == category.id

    tags = db.session.scalars(select(Tag.name)).all()
    assert sorted(tags) == ["code-editors", "vim"]
    assert sorted(tag.name for tag in question.tags) == ["code-editors", "vim"]

    user = db.session.scalar(select(User).where(User.email == "cata@example.com"))
    assert user is not None
    assert question.user_id == user.id

    post = db.session.scalar(select(Post).where(Post.id == question.id))
    assert post is not None

    assert post.id == question.id
    assert post.type == "question"
