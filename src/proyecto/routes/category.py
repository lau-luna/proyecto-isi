from flask import Blueprint, render_template
from sqlalchemy import distinct, func, select

from proyecto.extensions import db
from proyecto.models.Answer import Answer
from proyecto.models.Category import Category
from proyecto.models.Question import Question
from proyecto.utils.index_forms import LogOutForm

bp = Blueprint("category", __name__, template_folder="templates")


@bp.route("/categories", methods=["GET"])
def categories():
    logout_form = LogOutForm()

    rows = db.session.execute(
        select(
            Category,
            func.count(distinct(Question.id)),
            func.count(Answer.id),
        )
        .outerjoin(Question, Question.category_id == Category.id)
        .outerjoin(Answer, Answer.question_id == Question.id)
        .group_by(Category.id)
        .order_by(Category.name)
    ).all()

    return render_template(
        "category/categories.html", rows=rows, logout_form=logout_form
    )


@bp.route("/category/<int:id>", methods=["GET"])
def category(id):
    logout_form = LogOutForm()

    category = db.session.scalar(select(Category).where(Category.id == id))
    questions_by_category = db.session.scalars(
        select(Question)
        .join(Category)
        .where(Category.id == id)
        .order_by(Question.published_at.desc())
    ).all()

    return render_template(
        "category/category.html",
        category=category,
        questions_by_category=questions_by_category,
        logout_form=logout_form,
    )
