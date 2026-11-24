from flask import Blueprint, render_template
from sqlalchemy import select

from proyecto.extensions import db
from proyecto.models.Category import Category
from proyecto.routes.user import login_required
from proyecto.utils.index_forms import LogOutForm
from proyecto.utils.question_forms import AddQuestionForm

bp = Blueprint("question", __name__, template_folder="templates")


@bp.route("/question", methods=["GET", "POST"])
@login_required
def post_question():
    form = AddQuestionForm()
    form.category.choices = [
        (category.id, category.name)
        for category in db.session.scalars(
            select(Category).order_by(Category.name)
        ).all()
    ]
    return (
        render_template(
            "question/add-question-form.html",
            form=form,
            logout_form=LogOutForm(),
        ),
        200,
    )
