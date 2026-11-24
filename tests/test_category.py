from sqlalchemy import select

from proyecto.models.Category import Category
from proyecto.seeds import seed_categories


def test_categories_are_seeded_and_idempotent(session):
    seed_categories()

    initial_names = sorted(session.scalars(select(Category.name)).all())

    assert initial_names

    seed_categories()
    assert sorted(session.scalars(select(Category.name)).all()) == initial_names
