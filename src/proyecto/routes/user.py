from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound

bp = Blueprint('user', __name__,
                        template_folder='templates')

@bp.route('/user/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        return "post de register"
    elif request.method == "GET":
        return "get de register"

    return "error"
