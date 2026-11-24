from flask import Blueprint, jsonify, request
from sqlalchemy import select

from proyecto.extensions import db
from proyecto.models.Tag import Tag

bp = Blueprint("tags", __name__, template_folder="templates")


@bp.route("/tags/search", methods=["GET"])
def search_tags():
    query = request.args.get("q", "").strip().casefold()

    if not query:
        return jsonify([])

    tags = db.session.scalars(
        select(Tag.name)
        .where(Tag.name.startswith(query, autoescape=True))
        .order_by(Tag.name)
        .limit(10)
    ).all()

    return jsonify(tags)
