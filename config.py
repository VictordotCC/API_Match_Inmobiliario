import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()

distance_bleed = 200

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    CORS_HEADERS = '*'
    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')
    EXPIRES_DATE = os.environ.get('EXPIRES_DATE')
    SECRET_KEY = os.environ.get('KEY')
    SECRET_IV = os.environ.get('IV')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    SALT = os.environ.get('SALT')

    #EMAIL SETTINGS
    MAIL_DEFAULT_SENDER = "noreply@match.inmobiliario.cl"
    MAIL_SERVER = "smtp.imitate.email"
    MAIL_PORT = 587
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEBUG = False
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    #JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=30)

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = False

class ProdConfig(Config):
    DEBUG = False