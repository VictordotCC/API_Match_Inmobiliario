from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from config import DevConfig, TestConfig, ProdConfig

import geopandas as gpd

global gdf
gdf = gpd.read_file('app/helpers/shapefiles/comunas.shp')
gdf_wgs84 = gdf.to_crs(epsg=4326)

db = SQLAlchemy()
migrate = Migrate()

config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type"]}})

    app.config.from_object(config['prod'])

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import routes
    app.register_blueprint(routes.app)

    return app