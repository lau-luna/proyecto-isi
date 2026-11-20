import os

from flask import Flask, render_template

from proyecto.config import config
from proyecto.extensions import db, migrate

from . import models  # noqa: F401  (registra los modelos en db.metadata)

from proyecto.routes.user import bp as user_bp

def create_app(environment="development"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # configure this app whithin the environment
    app.config.from_object(config[environment])

    db.init_app(app)
    migrate.init_app(app, db)


    app.register_blueprint(user_bp)
    
    @app.route("/")
    @app.route("/<name>")
    def index(name=None):
        return render_template("index.html", person=name)

    return app
