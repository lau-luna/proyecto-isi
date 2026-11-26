import re

from flask import Blueprint, abort, g, redirect, request, url_for
from sqlalchemy.exc import IntegrityError

from proyecto.extensions import db
from proyecto.models.Answer import Answer
from proyecto.models.Post import Post
from proyecto.models.Question import Question
from proyecto.routes.user import login_required

bp = Blueprint("vote", __name__)

# A same-site path: starts with a single "/" and only has ordinary URL
# characters. Backslashes, spaces and control characters (e.g. a tab, which
# browsers drop, turning "/\t/evil.com" into "//evil.com") are rejected.
SAFE_NEXT_PATH = re.compile(r"/(?!/)[A-Za-z0-9/_.~%?=&+-]*")


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
    if SAFE_NEXT_PATH.fullmatch(next_url):
        return redirect(next_url)
    question = post if isinstance(post, Question) else post.question
    return redirect(url_for("question.question_detail", question_id=question.id))


def save_vote() -> None:
    try:
        db.session.commit()
    except IntegrityError:
        # Two requests of the same user raced and the database kept only one
        # vote (one vote per user and post). Nothing else to do.
        db.session.rollback()


@bp.route("/posts/<int:post_id>/upvote", methods=["POST"])
@login_required
def upvote(post_id):
    post = find_votable_post(post_id)
    post.upvote(g.user)
    save_vote()
    return redirect_back(post)


@bp.route("/posts/<int:post_id>/downvote", methods=["POST"])
@login_required
def downvote(post_id):
    post = find_votable_post(post_id)
    post.downvote(g.user)
    save_vote()
    return redirect_back(post)
