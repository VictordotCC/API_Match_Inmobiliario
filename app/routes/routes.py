from flask import Blueprint, jsonify, request
from config import Config
from app.models import *

from app.helpers import refreshtoken, fillDB_PI
from geoalchemy2 import functions as func
from app.helpers import leer_georef
import json

app = Blueprint('main', __name__)

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

@app.route('/about')
def about():
    return jsonify({'message': 'About page'})


#Ejemplo QUERY JSON field:
# data = Target.query.order_by(Target.product['salesrank'])


#RUTAS DE ADMIN
#TODO: Implementar tokens de seguridad
@app.route('/refresh', methods=['GET'])
def refresh():
    from app.helpers import refreshtoken
    access_token = refreshtoken.refresh_token()
    return jsonify({'message': 'Token actualizado'})

@app.route('/testgeo', methods=['GET'])
def testgeo():
    geodata = leer_georef.leer_georef(-33.461082369999005, -70.6540934777483)
    return jsonify(geodata)

@app.route('/info_portalinmobiliario/<string:comuna>', methods=['GET'])
def info_portalinmobiliario(comuna):
    comunaConsulta = comuna
    try:
        access_token = refreshtoken.refresh_token()
        responses = fillDB_PI.fillDB_PI(access_token, comunaConsulta)
        for response in responses:
            for result in response['results']:
                id_vivienda = result['id']
                #Check if vivienda already exists
                viviendaQ = Vivienda.query.filter_by(id_vivienda=id_vivienda).first()
                if viviendaQ is not None:
                    continue
                vivienda = Vivienda()
                vivienda.id_vivienda = id_vivienda
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
                links = result['permalink'] if isinstance(result['permalink'], list) else [result['permalink']]
                vivienda.links_contacto = json.dumps(links)       
                #Obtener comuna, region, coudad
                geodata = leer_georef.leer_georef(vivienda.latitud, vivienda.longitud)
                #Obtener id_comuna, id_region, id_ciudad
                region = Region.query.filter_by(nombre_region=geodata['region']).first()
                if region is None:
                    region = Region(nombre_region=geodata['region'])
                    region.save()
                vivienda.id_region = region.id_region
                ciudad = Ciudad.query.filter_by(nom_ciudad=geodata['ciudad']).first()
                if ciudad is None:
                    ciudad = Ciudad(nom_ciudad=geodata['ciudad'], id_region=region.id_region)
                    ciudad.save()
                vivienda.id_ciudad = ciudad.id_ciudad
                comuna = Comuna.query.filter_by(nom_comuna=geodata['comuna']).first()
                if comuna is None:
                    comuna = Comuna(nom_comuna=geodata['comuna'], id_ciudad=ciudad.id_ciudad, id_region=region.id_region)
                    comuna.save()
                vivienda.id_comuna = comuna.id_comuna
                #Obtener id_vecindario
                vecindario = result['location']['neighborhood']['name']
                vecindarioQ = Vecindario.query.filter_by(nom_vecindario=vecindario).first()
                if vecindarioQ is None:
                    vecindarioQ = Vecindario(nom_vecindario=vecindario, id_comuna=comuna.id_comuna, id_ciudad=ciudad.id_ciudad, id_region=region.id_region)
                    vecindarioQ.save()
                vivienda.id_vecindario = vecindarioQ.id_vecindario
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
                #Logica para guardar imagenes
                imagen = Imagen()
                imagen.url= result['thumbnail']
                imagen.id_vivienda = vivienda.id_vivienda
                #Arma el id de la imagen de tal forma que contenga IMG + los ultimos 7 digitos del id de la vivienda
                imagen.id = "IMG"+str(vivienda.id_vivienda)[-7:]
                vivienda.fecha_creacion = datetime.datetime.now(datetime.timezone.utc)                  
                vivienda.save()
    except Exception as e:
        return jsonify({'message': f'Error: {e}'})

    return jsonify({'message': f'Informacion de Portal Inmobiliario de {comunaConsulta} importada correctamente'})

@app.route('/info_test')
def info_test():
    return jsonify({'message': Config.EXPIRES_DATE})

