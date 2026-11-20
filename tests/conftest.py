import pytest

from proyecto import create_app
from proyecto.extensions import db


@pytest.fixture(scope="session")
def app():
    # creamos una aplicacion con entorno testing
    app = create_app("testing")
    yield app


## Cliente de pruebas para peticiones HTTP
@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


# Crea las tablas antes de cada test y despues las borra
@pytest.fixture(scope="function")
def init_database(app):
    with app.app_context():
        db.create_all()
        yield
        db.drop_all()


# Sesion para usar directo en los tests
@pytest.fixture(scope="function")
def session(app, init_database):
    with app.app_context():
        yield db.session
