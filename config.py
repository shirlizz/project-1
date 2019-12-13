class Config(object):
    SECRET_KEY = 'secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = ''
class DevelopmentConfig(Config):
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost:5432/book'
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    ENV='development'
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost:5432/book'