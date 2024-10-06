import os
from dotenv import load_dotenv

load_dotenv()



class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    CORS_HEADERS = '*'

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = False

class ProdConfig(Config):
    DEBUG = False