from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import aliased

from proyecto.extensions import db
from proyecto.models.Answer import Answer
from proyecto.models.Question import SORT_OPTIONS, Question
from proyecto.models.QuestionTag import question_tag
from proyecto.models.Tag import Tag
from proyecto.utils.index_forms import LogOutForm

bp = Blueprint("tags", __name__, template_folder="templates")


@bp.route("/tags/", methods=["GET"])
def tags():
    logout_form = LogOutForm()
    answer = aliased(Answer, flat=True)

    rows = db.session.execute(
        select(
            Tag,
            func.count(distinct(Question.id)),
            func.count(answer.id),
        )
        .outerjoin(question_tag, question_tag.c.tag_id == Tag.id)
        .outerjoin(Question, Question.id == question_tag.c.question_id)
        .outerjoin(answer, answer.question_id == Question.id)
        .group_by(Tag.id)
        .order_by(Tag.name.asc())
    ).all()
    return render_template("tag/tags.html", rows=rows, logout_form=logout_form)


@bp.route("/tag/<int:id>", methods=["GET"])
def tag(id):
    logout_form = LogOutForm()

    tag = db.session.scalar(select(Tag).where(Tag.id == id))
    sort = request.args.get("sort", "score")
    if sort not in SORT_OPTIONS:
        sort = "score"
    questions_by_tag = db.session.scalars(
        select(Question)
        .where(Question.tags.any(Tag.id == id))
        .order_by(*Question.sort_order(sort))
    ).all()

    return render_template(
        "tag/tag.html",
        tag=tag,
        questions_by_tag=questions_by_tag,
        sort=sort,
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
