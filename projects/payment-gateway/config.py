import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# settings.py

load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = ['your-email@example.com']
    # mail settings
    MAIL_SERVER = 'mail.tritel.co.ke'
    MAIL_PORT = 587
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False

    # gmail authentication
    MAIL_USERNAME = "tesfa@tritel.co.ke"
    MAIL_PASSWORD = 'T3sf@0z3M70'

    # mail accounts
    MAIL_DEFAULT_SENDER = 'tesfa@tritel.co.ke'

    PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
    UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    JSON_AS_ASCII = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SERVER_NAME = 'localhost'