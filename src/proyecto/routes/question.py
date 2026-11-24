from flask import Blueprint, redirect, render_template, session, url_for
from sqlalchemy import select

from proyecto.extensions import db
from proyecto.models.Category import Category
from proyecto.models.Question import Question
from proyecto.models.Tag import Tag
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

    if form.validate_on_submit():
        title = form.title.data.strip()
        body = form.body.data.strip()
        tags = (form.tags.data or "").strip()

        category = form.category.data

        # tags processing
        split_tags = tags.lower().split(" ")
        tags = []

        for tag in split_tags:
            db_tag = db.session.scalar(select(Tag).where(Tag.name == tag))
            if db_tag is None:
                db_tag = Tag(name=tag)
                db.session.add(db_tag)
            tags.append(db_tag)
        db.session.commit()

        question = Question(
            title=title,
            category_id=category,
            body=body,
            user_id=session["user_id"],
            tags=tags,
        )
        db.session.add(question)
        db.session.commit()

        # TODO: redirect to the question link using the new id
        return redirect(url_for("index"))

    return (
        render_template(
            "question/add-question-form.html",
            form=form,
            logout_form=LogOutForm(),
        ),
        400 if form.is_submitted() else 200,
    )
