from flask import Blueprint, render_template
from sqlalchemy import select

from proyecto.extensions import db
from proyecto.models.Category import Category
from proyecto.models.Question import Question
from proyecto.utils.index_forms import LogOutForm

bp = Blueprint("index", __name__, template_folder="templates")


@bp.route("/")
def index():
    logout_form = LogOutForm()

    latest_questions = db.session.scalars(
        select(Question)
        .join(Category)
        .order_by(*Question.sort_order("newest"))
        .limit(10)
    )

    return render_template(
        "index.html",
        latest_questions=latest_questions,
        logout_form=LogOutForm(),
    )
    return render_template("index.html", logout_form=logout_form)
