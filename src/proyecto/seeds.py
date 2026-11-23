from sqlalchemy import inspect, select

from proyecto.extensions import db
from proyecto.models.Category import Category

"""
Seedea 21 categorias a la tabla category.
Se ejecuta cada vez que se inicia la aplicacion.
Es idempotente, solo inserta las categorias si no existen previamente.
"""


def seed_categories():
    if not inspect(db.engine).has_table(Category.__tablename__):
        return

    categories = [
        "Technology",
        "Programming",
        "Science",
        "Mathematics",
        "History",
        "Geography",
        "Literature",
        "Arts & Culture",
        "Music",
        "Movies & TV",
        "Video Games",
        "Sports",
        "Health & Fitness",
        "Food & Cooking",
        "Travel",
        "Education",
        "Career & Work",
        "Personal Finance",
        "Home & Garden",
        "Lifestyle",
        "Other",
    ]

    for cat_name in categories:
        if db.session.scalar(select(Category).where(Category.name == cat_name)) is None:
            db.session.add(Category(cat_name))

    db.session.commit()
