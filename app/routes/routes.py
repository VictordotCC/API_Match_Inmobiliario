import requests

from flask import Blueprint, jsonify
from config import Config
from app.models import *

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
@app.route('/refresh')
def refresh():
    from app.helpers import refreshtoken
    access_token = refreshtoken.refresh_token()
    return jsonify({'message': 'Token actualizado'})

@app.route('/testgeo')
def testgeo():
    from app.helpers import leer_georef
    geodata = leer_georef.leer_georef(-33.461082369999005, -70.6540934777483)
    return jsonify(geodata)

@app.route('/info_portalinmobiliario')
def info_portalinmobiliario():
    return jsonify({'message':'No implementado'})
    from app.helpers import refreshtoken, fillDB_PI
    from geoalchemy2 import functions as func
    access_token = refreshtoken.refresh_token()
    responses = fillDB_PI.fillDB_PI(access_token, 'La Florida')
    for response in responses:
        for result in response['results']:
            vivienda = Vivienda()
            if result['sale_price']['currency_id'] == 'CLF':
                vivienda.precio_uf = result['sale_price']['amount']
            else:
                #TODO: Obtener valor de UF
                valor_uf = 38000
                vivienda.precio_uf = result['sale_price']['amount'] / valor_uf
            vivienda.nombre_propiedad = result['title']
            vivienda.descripcion = result['location']['address_line']
            vivienda.latitud = result['location']['latitude']
            vivienda.longitud = result['location']['longitude']
            vivienda.ubicacion = func.ST_GeomFromText(f'POINT({vivienda.longitud} {vivienda.latitud})', 4326)
            vivienda.links_contacto = jsonify(result['permalink'])
            
            regionQ = Region.query.filter(Region.nombre == result['location']['state']['name']).first()
            if regionQ:
                vivienda.id_region = regionQ.id_region
            else:
                pass

            comunaQ = Comuna.query.filter(Comuna.nombre == result['location']['city']['name']).first()
            if comunaQ:
                vivienda.id_comuna = comunaQ.id_comuna
                vivienda.id_ciudad = comunaQ.id_ciudad
                vivienda.id_region = comunaQ.id_region
            else:
                #TODO: obtener datos de la comuna
                pass

            for attrib in result['attributes']:
                if attrib['id'] == 'MAX_TOTAL_AREA' or attrib['id'] == 'TOTAL_AREA':
                    vivienda.area_total = attrib['value_struct']['number']
                if attrib['id'] == 'MAX_BEDROOMS' or attrib['id'] == 'BEDROOMS':
                    vivienda.habitaciones = attrib['value_name']
                if attrib['id'] == 'PROPERTY_TYPE':
                    if attrib['value_name'] == 'Casa':
                        vivienda.tipo_vivienda = 1
                    elif attrib['value_name'] == 'Departamento':
                        vivienda.tipo_vivienda = 0
                if attrib['id'] == 'ITEM_CONDITION':
                    vivienda.condicion = attrib['value_name']
                if attrib['id'] == 'OPERATION':
                    if attrib['value_name'] == 'Venta':
                        vivienda.tipo_operacion = 0
                    elif attrib['value_name'] == 'Arriendo':
                        vivienda.tipo_operacion = 1
                if attrib['id'] == 'FULL_BATHROOMS' or attrib['id'] == 'MAX_BATHROOMS':
                    vivienda.banos = attrib['value_name']
                if attrib['id'] == 'COVERED_AREA' or attrib['id'] == 'MAX_COVERED_AREA':
                    vivienda.area_construida = attrib['value_struct']['number']

    return jsonify({'message': 'Informacion de Portal Inmobiliario'})

@app.route('/info_test')
def info_test():
    return jsonify({'message': Config.EXPIRES_DATE})

