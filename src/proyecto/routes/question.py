from flask import Blueprint, redirect, render_template, request, session, url_for
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

    if request.method == "GET":
        preselected = request.args.get("category", type=int)
        valid_ids = {id for id, _ in form.category.choices}
        if preselected in valid_ids:
            form.category.data = preselected

        tag_ids = request.args.getlist("tag", type=int)
        if tag_ids:
            tag_names = db.session.scalars(
                select(Tag.name).where(Tag.id.in_(tag_ids)).order_by(Tag.name)
            ).all()
            form.tags.data = " ".join(tag_names)

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
        return redirect(url_for("index.index"))

    return (
        render_template(
            "question/add-question-form.html",
            form=form,
            logout_form=LogOutForm(),
        ),
        400 if form.is_submitted() else 200,
    )


@bp.route("/questions", methods=["GET"])
def questions():
    categories = db.session.scalars(select(Category)).all()
    latest_questions = db.session.scalars(select(Question).join(Category).limit(10))

    return render_template(
        "question/questions.html",
        categories=categories,
        latest_questions=latest_questions,
        logout_form=LogOutForm(),
    )


@bp.route("/questions/<int:question_id>", methods=["GET"])
def question_detail(question_id):
    question = db.get_or_404(Question, question_id)

    return render_template(
        "question/detail.html",
        question=question,
        logout_form=LogOutForm(),
    )
