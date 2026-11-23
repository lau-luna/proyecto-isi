from flask import Blueprint
from sqlalchemy import select

from proyecto.extensions import db

from proyecto.models.Category import Category

bp = Blueprint("category", __name__, template_folder="templates")

"""
Returns a list of Category with all the available categories
"""
@bp.route("/category", methods=["GET"])
def list_categories():
    categories = db.session.scalar(select(Category))
    return categories

"""
Adds a new category.
Only a moderator or administrator can do it.
"""
@bp.route("/category", methods=["POST"])
def add_category():
    return None
