from flask import Blueprint, render_template, request
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import aliased

from proyecto.extensions import db
from proyecto.models.Answer import Answer
from proyecto.models.Category import Category
from proyecto.models.Question import SORT_OPTIONS, Question
from proyecto.utils.index_forms import LogOutForm

bp = Blueprint("category", __name__, template_folder="templates")


@bp.route("/categories", methods=["GET"])
def categories():
    logout_form = LogOutForm()

    answer = aliased(Answer, flat=True)

    rows = db.session.execute(
        select(
            Category,
            func.count(distinct(Question.id)),
            func.count(answer.id),
        )
        .outerjoin(Question, Question.category_id == Category.id)
        .outerjoin(answer, answer.question_id == Question.id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
    ).all()
    return render_template(
        "category/categories.html", rows=rows, logout_form=logout_form
    )


@bp.route("/category/<int:id>", methods=["GET"])
def category(id):
    logout_form = LogOutForm()

    category = db.session.scalar(select(Category).where(Category.id == id))
    sort = request.args.get("sort", "score")
    if sort not in SORT_OPTIONS:
        sort = "score"
    questions_by_category = db.session.scalars(
        select(Question)
        .join(Category)
        .where(Category.id == id)
        .order_by(*Question.sort_order(sort))
    ).all()

    return render_template(
        "category/category.html",
        category=category,
        questions_by_category=questions_by_category,
        sort=sort,
        logout_form=logout_form,
    )
