from flask import Blueprint, jsonify
from config import Config

app = Blueprint('main', __name__)

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

@app.route('/about')
def about():
    return jsonify({'message': 'About page'})


#Ejemplo QUERY JSON field:
# data = Target.query.order_by(Target.product['salesrank'])

#Ejemplo Ingreso ubicacion desde latitud y longitud
#lat = 37.7749295
#lon = -122.4194155
#from Geoalchemy2 import func
#ubicacion = func.ST_GeomFromText(f'POINT({lon} {lat})', 4326)
#vivienda(ubicacion=ubicacion)
#vivienda.save()

#RUTAS DE ADMIN
#TODO: Implementar tokens de seguridad

@app.route('/info_portalinmobiliario')
def info_portalinmobiliario():
    from app.helpers import refreshtoken, fillDB_PI
    access_token = refreshtoken.refresh_token()
    fillDB_PI.fillDB_PI(access_token, 'La Florida')
    return jsonify({'message': 'Informacion de Portal Inmobiliario'})

@app.route('/info_test')
def info_test():
    return jsonify({'message': Config.EXPIRES_DATE})

