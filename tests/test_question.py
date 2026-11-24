from test_auth import create_test_user

from proyecto.models.Category import Category


def test_question_form_renders(client, session):
    create_test_user(session)
    session.add(Category("Programming"))
    session.commit()
    client.post(
        "/user/login",
        data={"email": "cata@example.com", "password": "secretpassword"},
    )

    response = client.get("/question")

    assert response.status_code == 200
    assert b"Ask a question" in response.data
    assert b'name="title"' in response.data
    assert b'name="category"' in response.data
    assert b"Programming" in response.data
    assert b'name="body"' in response.data
    assert b'name="tags"' in response.data
    assert b"Ask question" in response.data
    assert b"Log out" in response.data
