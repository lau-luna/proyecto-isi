import os

from flask import Flask, render_template
from sqlalchemy.orm import sessionmaker

from config import config
from proyecto.extensions import Base, create_db_engine

from . import models  # noqa: F401  (registra los modelos en Base.metadata)


def create_app(environment="development"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # configure this app whithin the environment
    app.config.from_object(config[environment])

    # una sola conexión y un solo sessionmaker por aplicación
    engine = create_db_engine(app.config["DATABASE_URL"])
    app.extensions["db_engine"] = engine
    app.extensions["db_session"] = sessionmaker(bind=engine, expire_on_commit=False)

    @app.teardown_appcontext
    def close_db_session(exc):
        from flask import g

        session = g.pop("db", None)
        if session is not None:
            session.close()

    @app.cli.command("init-db")
    def init_db_command():
        """Crea todas las tablas (solo para desarrollo)."""
        Base.metadata.create_all(engine)

    @app.route("/")
    @app.route("/<name>")
    def index(name=None):
        return render_template("index.html", person=name)

    return app
