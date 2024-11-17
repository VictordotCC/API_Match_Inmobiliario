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

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=30)

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = False

class ProdConfig(Config):
    DEBUG = False