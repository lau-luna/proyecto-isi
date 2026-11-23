from flask import Blueprint

from proyecto.extensions import db
from proyecto.routes.user import login_required

bp = Blueprint("question", __name__, template_folder="templates")

@bp.route("/question", methods=["POST"])
@login_required
def post_question():

