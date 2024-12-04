from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from app.helpers.notification import send_notification
from config import DevConfig, TestConfig, ProdConfig
import firebase_admin
from firebase_admin import credentials, firestore
import geopandas as gpd
import json
import os

global gdf
gdf = gpd.read_file('app/helpers/shapefiles/comunas.shp')
gdf_wgs84 = gdf.to_crs(epsg=4326)

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config.from_object(config['dev'])
    mail.init_app(app)
    
    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)

    if not firebase_admin._apps:
        cred = credentials.Certificate('/etc/secrets/firebase.json')
        #cred = credentials.Certificate('firebase.json')
        firebase_admin.initialize_app(cred)

    from app.routes import routes
    app.register_blueprint(routes.app)    
    

    return app