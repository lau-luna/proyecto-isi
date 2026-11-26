from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import select

from proyecto.extensions import db
from proyecto.models.Question import Question
from proyecto.models.Tag import Tag
from proyecto.utils.index_forms import LogOutForm

bp = Blueprint("tags", __name__, template_folder="templates")


@bp.route("/tags/", methods=["GET"])
def tags():
    logout_form = LogOutForm()

    tags = db.session.scalars(select(Tag).order_by(Tag.name)).all()

    return render_template("tag/tags.html", tags=tags, logout_form=logout_form)


@bp.route("/tag/<int:id>", methods=["GET"])
def tag(id):
    logout_form = LogOutForm()

    tag = db.session.scalar(select(Tag).where(Tag.id == id))
    questions_by_tag = db.session.scalars(
        select(Question)
        .where(Question.tags.any(Tag.id == id))
        .order_by(Question.published_at.desc())
    ).all()

    return render_template(
        "tag/tag.html",
        tag=tag,
        questions_by_tag=questions_by_tag,
        logout_form=logout_form,
    )


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
