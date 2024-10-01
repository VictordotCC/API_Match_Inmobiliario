from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevConfig, TestConfig, ProdConfig

db = SQLAlchemy()
migrate = Migrate()

config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}

def create_app():
    app = Flask(__name__)
    app.config.from_object(config['prod'])

    #db.init_app(app)
    #migrate.init_app(app, db)

    from app.routes import routes
    app.register_blueprint(routes.app)

    return app