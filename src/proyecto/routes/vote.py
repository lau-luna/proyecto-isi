from flask import Blueprint, abort, g, redirect, request, url_for

from proyecto.extensions import db
from proyecto.models.Answer import Answer
from proyecto.models.Post import Post
from proyecto.models.Question import Question
from proyecto.routes.user import login_required

bp = Blueprint("vote", __name__)


def find_votable_post(post_id: int) -> Question | Answer:
    """Only questions and answers can be voted (replies cannot)."""
    post = db.get_or_404(Post, post_id)
    if not isinstance(post, Question | Answer):
        abort(404)
    return post


def redirect_back(post: Question | Answer):
    """Go back to the page the vote came from, or to the question."""
    next_url = request.form.get("next", "")
    # Only same-site paths, to avoid redirecting to another website.
    if next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)
    question = post if isinstance(post, Question) else post.question
    return redirect(url_for("question.question_detail", question_id=question.id))


@bp.route("/posts/<int:post_id>/upvote", methods=["POST"])
@login_required
def upvote(post_id):
    post = find_votable_post(post_id)
    post.upvote(g.user)
    db.session.commit()
    return redirect_back(post)


@bp.route("/posts/<int:post_id>/downvote", methods=["POST"])
@login_required
def downvote(post_id):
    post = find_votable_post(post_id)
    post.downvote(g.user)
    db.session.commit()
    return redirect_back(post)
