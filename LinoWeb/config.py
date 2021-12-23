import os

class Config(object):
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'linomtl'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/lino_ads'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    db_user = 'postgres'
    db_pass = 'postgres'
    db_host = '18.233.93.152'
    # db_host = 'localhost'
    db_name = 'lino_ads'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
                                db_user, db_pass, db_host, db_name)

class TestConfig(Config):
    TESTING = False

    db_user = 'postgres'
    db_pass = 'postgres'
    db_host = 'localhost'
    db_name = 'lino_test'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
                                db_user, db_pass, db_host, db_name)

class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

configs = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig,
}