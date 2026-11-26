from flask import (
    Blueprint,
    abort,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import select

from proyecto.extensions import db
from proyecto.models.Answer import Answer
from proyecto.models.Category import Category
from proyecto.models.HumanAuthorFactory import HumanAuthorFactory
from proyecto.models.Question import Question
from proyecto.models.Tag import Tag
from proyecto.routes.user import login_required
from proyecto.utils.accept_forms import AcceptAnswerForm
from proyecto.utils.answer_forms import AnswerForm
from proyecto.utils.index_forms import LogOutForm
from proyecto.utils.question_forms import AddQuestionForm
from proyecto.utils.reply_forms import ReplyForm

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
    search = request.args.get("q", default="").strip()

    query = select(Question).order_by(*Question.sort_order())
    if search:
        # Case-insensitive match on the question title or body.
        pattern = f"%{search}%"
        query = query.where(
            Question.title.ilike(pattern) | Question.body.ilike(pattern)
        )
    else:
        query = query.limit(10)

    return render_template(
        "question/questions.html",
        questions=db.session.scalars(query).all(),
        search=search,
        logout_form=LogOutForm(),
    )


@bp.route("/questions/<int:question_id>", methods=["GET"])
def question_detail(question_id):
    question = db.get_or_404(Question, question_id)

    return render_template(
        "question/detail.html",
        question=question,
        answer_form=AnswerForm(),
        reply_form=ReplyForm(),
        accept_form=AcceptAnswerForm(),
        logout_form=LogOutForm(),
    )


@bp.route("/questions/<int:question_id>/answers", methods=["POST"])
@login_required
def answer_question(question_id):
    question = db.get_or_404(Question, question_id)
    form = AnswerForm()

    if form.validate_on_submit():
        # The logged-in user is the author of a human answer.
        question.add_answer(form.body.data.strip(), HumanAuthorFactory(g.user))
        db.session.commit()
        return redirect(url_for("question.question_detail", question_id=question.id))

    return (
        render_template(
            "question/detail.html",
            question=question,
            answer_form=form,
            reply_form=ReplyForm(),
            accept_form=AcceptAnswerForm(),
            logout_form=LogOutForm(),
        ),
        400,
    )


@bp.route("/answers/<int:answer_id>/replies", methods=["POST"])
@login_required
def reply_to_answer(answer_id):
    answer = db.get_or_404(Answer, answer_id)
    question = answer.question
    form = ReplyForm()

    if form.validate_on_submit():
        answer.add_reply(form.body.data.strip(), HumanAuthorFactory(g.user))
        db.session.commit()
        return redirect(url_for("question.question_detail", question_id=question.id))

    return (
        render_template(
            "question/detail.html",
            question=question,
            answer_form=AnswerForm(),
            reply_form=form,
            # Tells the template which answer's reply form has the errors.
            reply_answer_id=answer.id,
            accept_form=AcceptAnswerForm(),
            logout_form=LogOutForm(),
        ),
        400,
    )


@bp.route("/answers/<int:answer_id>/accept", methods=["POST"])
@login_required
def accept_answer(answer_id):
    answer = db.get_or_404(Answer, answer_id)
    question = answer.question

    if not AcceptAnswerForm().validate_on_submit():
        abort(400)

    try:
        question.accept_answer(answer, g.user)
    except PermissionError:
        # Only the question author can accept answers.
        abort(403)

    db.session.commit()
    return redirect(url_for("question.question_detail", question_id=question.id))


@bp.route("/answers/<int:answer_id>/unaccept", methods=["POST"])
@login_required
def unaccept_answer(answer_id):
    answer = db.get_or_404(Answer, answer_id)
    question = answer.question

    if not AcceptAnswerForm().validate_on_submit():
        abort(400)

    try:
        question.unaccept_answer(answer, g.user)
    except PermissionError:
        # Only the question author can remove the acceptance.
        abort(403)

    db.session.commit()
    return redirect(url_for("question.question_detail", question_id=question.id))
