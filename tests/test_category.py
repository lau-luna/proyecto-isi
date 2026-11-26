from sqlalchemy import select

from proyecto.models.Category import Category
from proyecto.seeds import seed_categories


def test_categories_are_seeded_and_idempotent(session):
    seed_categories()

    initial_names = sorted(session.scalars(select(Category.name)).all())

    assert initial_names

    seed_categories()
    assert sorted(session.scalars(select(Category.name)).all()) == initial_names


def test_categories_page_lists_categories_in_alphabetical_order(client, session):
    session.add_all([Category("Technology"), Category("Programming")])
    session.commit()

    response = client.get("/categories")

    assert response.status_code == 200
    assert b"Technology" in response.data
    assert b"Programming" in response.data
    assert response.data.index(b"Programming") < response.data.index(b"Technology")
    assert b"#n" in response.data
    assert b"Questions" in response.data
    assert b"Answers" in response.data
