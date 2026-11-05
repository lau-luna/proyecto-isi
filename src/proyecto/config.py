import os


class Config:
    TESTING = False

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    DATABASE_URL = "postgresql://user@localhost/foo"


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    ENV = "development"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATABASE_URL = "sqlite:////tmp/foo.db"


class TestingConfig(Config):
    DATABASE_URL = "sqlite:///:memory:"
    TESTING = True
    SECRET_KEY = "TEST"


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
