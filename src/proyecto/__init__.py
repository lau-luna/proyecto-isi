import os

from flask import Flask, render_template

from config import config


def create_app(environment="development"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # configure this app whithin the environment
    app.config.from_object(config[environment])

    @app.route("/")
    @app.route("/<name>")
    def index(name=None):
        return render_template("index.html", person=name)

    return app
