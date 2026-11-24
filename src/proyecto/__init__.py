import os

from flask import Flask, g, render_template, session
from flask_wtf.csrf import CSRFProtect

from proyecto.config import config
from proyecto.extensions import db, migrate
from proyecto.models.User import User
from proyecto.routes.question import bp as question_bp
from proyecto.routes.tag import bp as tag_bp
from proyecto.routes.user import bp as user_bp
from proyecto.seeds import seed_categories
from proyecto.utils.index_forms import LogOutForm

from . import models  # noqa: F401  (registra los modelos en db.metadata)

csrf = CSRFProtect()


def create_app(environment="development"):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    csrf.init_app(app)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # configure this app whithin the environment
    app.config.from_object(config[environment])
    config[environment].init_app(app)

    # database migration and seeding
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        seed_categories()

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        if user_id is None:
            g.user = None
        else:
            g.user = db.session.get(User, user_id)

    # blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(question_bp)

    @app.route("/")
    @app.route("/<name>")
    def index(name=None):
        logout_form = LogOutForm()
        return render_template("index.html", logout_form=logout_form, person=name)

    return app
