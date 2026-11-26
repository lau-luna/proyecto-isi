import os

from flask import Flask, g, session
from flask_wtf.csrf import CSRFProtect

from proyecto.auth import user_has_role
from proyecto.config import config
from proyecto.extensions import db, migrate
from proyecto.models.Administrator import Administrator
from proyecto.models.Moderator import Moderator
from proyecto.models.User import User
from proyecto.routes.category import bp as category_bp
from proyecto.routes.index import bp as index_bp
from proyecto.routes.question import bp as question_bp
from proyecto.routes.tag import bp as tag_bp
from proyecto.routes.user import bp as user_bp
from proyecto.routes.vote import bp as vote_bp
from proyecto.seeds import seed_all

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
        seed_all()

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        if user_id is None:
            g.user = None
        else:
            g.user = db.session.get(User, user_id)

    # Make role checks available in every template, so templates can show
    # or hide actions with the same rule the views use, e.g.
    # {% if user_has_role(g.user, Moderator) %} ... {% endif %}
    app.jinja_env.globals.update(
        user_has_role=user_has_role,
        Moderator=Moderator,
        Administrator=Administrator,
    )

    # blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(vote_bp)

    app.register_blueprint(index_bp)

    return app
