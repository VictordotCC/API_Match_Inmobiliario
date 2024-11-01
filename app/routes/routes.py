from flask import Blueprint, jsonify, request
from flask_cors import CORS, cross_origin
import json

from geoalchemy2 import Geography
from geoalchemy2 import functions as func
from sqlalchemy import func as sqlfunc
from sqlalchemy import between
from sqlalchemy.orm import joinedload

from app.models import *
from app.helpers import refreshtoken, fillDB_PI
from app.helpers import leer_georef
from config import distance_bleed


app = Blueprint('main', __name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type"]}})

@app.after_request
def afer_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

@app.route('/')
def index():
    return jsonify({'message': 'API Match Inmobiliario V1.0'})

@app.route('/explorar', methods=['GET'])
def explorar():
    latitud = request.args.get('latitud')
    longitud = request.args.get('longitud')
    distancia = float(request.args.get('distancia', 1))
    referencia = f'SRID=4326;POINT({latitud} {longitud})'
    
    # Crear la consulta
    viviendas = db.session.query(
        Vivienda,
        func.ST_Distance(
            sqlfunc.cast(Vivienda.ubicacion, Geography),
            sqlfunc.cast(func.ST_GeographyFromText(referencia), Geography)
            ).label('distance')
        ).filter(
            func.ST_DWithin(
                sqlfunc.cast(Vivienda.ubicacion, Geography),
                sqlfunc.cast(func.ST_GeographyFromText(referencia), Geography),
                distancia * 1000  # Convertir a metros
        )
    ).all()
    for vivienda, distancia in viviendas:
        print(distancia)
    return jsonify([{**vivienda.serialize(), 'distancia': distancia} for vivienda, distancia in viviendas])


@app.route('/viviendas', methods=['GET', 'POST'])
def viviendas():
    if request.method == 'GET':
        vivienda = request.args.get('id_vivienda')
        vivienda = Vivienda.query.filter_by(id_vivienda=vivienda).first()
        if vivienda is not None:
            return jsonify(vivienda.serialize())
        else:
            return jsonify({'message': 'Vivienda no encontrada'})
    elif request.method == 'POST':
        #POST contiene las preferencias del usuario
        data = request.get_json()
        #return jsonify(data)
        #Realizar Query de viviendas segun las preferencias del usuario
        referencia = f'SRID=4326;POINT({data['ubicacion']['lon']} {data['ubicacion']['lat']})'
        distancia_m = int(data['preferencias']['distancia']) * 1000
        precio_desde = float(data['preferencias']['precio_uf_desde'])
        precio_hasta = float(data['preferencias']['precio_uf_hasta'])
        #campos excluyentes
        query = db.session.query(Vivienda)          
        query = query.filter(
            Vivienda.tipo_operacion == data['preferencias']['tipo_operacion'], # 1. Tipo de operacion
            Vivienda.tipo_vivienda == data['preferencias']['tipo_vivienda'], #2. Tipo de vivienda
            func.ST_DWithin(                                    # 4. Distancia
                sqlfunc.cast(Vivienda.ubicacion, Geography),
                sqlfunc.cast(func.ST_GeographyFromText(referencia), Geography),
                distancia_m + distance_bleed
            ),
            Vivienda.condicion == data['preferencias']['condicion'], # 9. Condicion
            Vivienda.tipo_subsidio == data['preferencias']['tipo_subsidio'] # 14. Tipo de subsidio
        )
        if precio_desde != 0 and precio_hasta != 0 and precio_desde-100 < precio_hasta+100:
            print('Precio desde:', precio_desde, 'Precio hasta:', precio_hasta)
            query = query.filter(
                Vivienda.precio_uf.between(precio_desde-100, precio_hasta+100)) # 3. Precio
            
        if data['preferencias']['habitaciones'] != 0:
            query = query.filter(Vivienda.habitaciones == data['preferencias']['habitaciones'])
        if data['preferencias']['area_construida'] != 0:
            query = query.filter(Vivienda.area_construida == data['preferencias']['area_construida'])
        if data['preferencias']['area_total'] != 0:
            query = query.filter(Vivienda.area_total == data['preferencias']['area_total'])
        if data['preferencias']['banos'] != 0:
            query = query.filter(Vivienda.banos == data['preferencias']['banos'])
        if data['preferencias']['estaciona'] != 0:
            #no se aplica por falta de datos
            #query = query.filter(Vivienda.estaciona == data['preferencias']['estaciona'])
            pass
        if data['preferencias']['bodega'] != 0:
            #no se aplica por falta de datos
            #query = query.filter(Vivienda.bodega == data['preferencias']['bodega'])
            pass
        if data['preferencias']['antiguedad'] != 0:
            #no se aplica por falta de datos
            #query = query.filter(Vivienda.antiguedad == data['preferencias']['antiguedad'])
            pass
        if data['preferencias']['pisos'] != 0:
            #no se aplica por falta de datos
            #query = query.filter(Vivienda.pisos == data['preferencias']['pisos']) 
            pass
        query = query.order_by(
            sqlfunc.abs(Vivienda.area_construida - data['preferencias']['area_construida']).asc(), # 6. Area Construida
            sqlfunc.abs(Vivienda.area_total - data['preferencias']['area_total']).asc(), # 7. Area Total
            sqlfunc.abs(Vivienda.banos - data['preferencias']['banos']).asc(), # 8. Baños
            sqlfunc.abs(Vivienda.estaciona - data['preferencias']['estaciona']).asc(), # 10. estacionamiento
            sqlfunc.abs(Vivienda.bodega - data['preferencias']['bodega']).asc(), # 11. bodega
            sqlfunc.abs(Vivienda.antiguedad - data['preferencias']['antiguedad']).asc(), # 12. antiguedad
            sqlfunc.abs(Vivienda.pisos - data['preferencias']['pisos']).asc(), # 13. pisos
            )

        viviendas = query.all()
        usuario = data['preferencias']['usuario']
        usuario_id = Usuario.query.filter_by(correo=usuario).first().id_usuario

        #Pre-fetch matches existentes
        ids_to_check = ['M' + str(usuario_id) + str(vivienda.id_vivienda) for vivienda in viviendas]
        existing_matches = set(match.id_match for match in Match.query.filter(Match.id_match.in_(ids_to_check)).all())
        matches = []
        
        for vivienda in viviendas:
            match_id = 'M'+ str(usuario_id) + str(vivienda.id_vivienda)
            if match_id not in existing_matches:
                match = Match()
                match.id_usuario = usuario_id
                match.id_vivienda = vivienda.id_vivienda
                match.fecha_coincidencia = datetime.datetime.now(datetime.timezone.utc)
                match.id_match = match_id
                matches.append(match)
        if matches:
            Match.bulk_save(matches)
        return jsonify({'message': 'Match actualizados '+ str(len(viviendas))})
    
@app.route('/viviendas_cercanas', methods=['GET'])
def viviendas_cercanas():
    latitud = request.args.get('lat')
    longitud = request.args.get('lon')
    distancia = 1000
    referencia = f'SRID=4326;POINT({longitud} {latitud})'

    viviendas = db.session.query(Vivienda, Imagen).join(Imagen, Imagen.id_vivienda == Vivienda.id_vivienda).filter(
        func.ST_DWithin(
            sqlfunc.cast(Vivienda.ubicacion, Geography),
            sqlfunc.cast(func.ST_GeographyFromText(referencia), Geography),
            distancia
            )
        ).all()
    viviendas_serializadas = [{**vivienda.serialize(), 'imagenes': [imagen.serialize()]} for vivienda, imagen in viviendas]
    return jsonify(viviendas_serializadas)

@app.route('/get_matches', methods=['GET'])
def get_matches():
    usuario = request.args.get('usuario')
    usuario_id = Usuario.query.filter_by(correo=usuario).first().id_usuario
    matches = Match.query.filter(
        Match.id_usuario == usuario_id,
        Match.visto == False).order_by(Match.fecha_coincidencia.desc()
        ).limit(20).all()

    viviendas_ids = [match.id_vivienda for match in matches]
    viviendas_dict = {v.id_vivienda: v for v in Vivienda.query.filter(Vivienda.id_vivienda.in_(viviendas_ids)).all()}
    imagenes_dict = {}
    for imagen in Imagen.query.filter(Imagen.id_vivienda.in_(viviendas_ids)).all():
        if imagen.id_vivienda not in imagenes_dict:
            imagenes_dict[imagen.id_vivienda] = []
        imagenes_dict[imagen.id_vivienda].append(imagen.serialize())

    viviendas = [
        {
            **viviendas_dict[match.id_vivienda].serialize(),
            'imagenes': imagenes_dict.get(match.id_vivienda, []),
            'id_match': match.id_match
        } for match in matches if match.id_vivienda in viviendas_dict
    ]
    return jsonify(viviendas)

@app.route('/marcar_visto', methods=['GET'])
def marcar_visto():
    id_match = request.args.get('id_match')
    match = Match.query.filter_by(id_match=id_match).first()
    if match is not None:
        match.visto = True
        match.update()
        return jsonify({'message': 'Match marcado como visto'})
    else:
        return jsonify({'message': 'Match no encontrado'})

#Ejemplo QUERY JSON field:
# data = Target.query.order_by(Target.product['salesrank'])


#RUTAS DE ADMIN
#TODO: Implementar tokens de seguridad
@app.route('/refresh', methods=['GET'])
def refresh():
    from app.helpers import refreshtoken
    access_token = refreshtoken.refresh_token()
    return jsonify({'message': 'Token actualizado'})

@app.route('/info_portalinmobiliario/<string:comuna>', methods=['GET'])
def info_portalinmobiliario(comuna):
    comunaConsulta = comuna
    try:
        access_token = refreshtoken.refresh_token()
        responses = fillDB_PI.fillDB_PI(access_token, comunaConsulta)
        for response in responses:
            for result in response['results']:
                print(result) #DEBUG
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
                address = result['location']['address_line']
                vivienda.latitud = result.get('location', {}).get('latitude', None)
                vivienda.longitud = result.get('location', {}).get('longitude', None)
                
                links = result['permalink'] if isinstance(result['permalink'], list) else [result['permalink']]
                vivienda.links_contacto = json.dumps(links)

                #Obtener comuna, region, coudad
                geodata = leer_georef.leer_georef(vivienda.latitud, vivienda.longitud, address)
                if geodata is None:
                    continue
                vivienda.ubicacion = func.ST_GeomFromText(f'POINT({vivienda.longitud} {vivienda.latitud})', 4326)
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
                vecindario = result.get('location', {}).get('neighborhood', {}).get('name', None)
                if vecindario is not None:
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
                        else:
                            vivienda.tipo_vivienda = 2
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
                imagen.url = result['thumbnail']
                imagen.id_vivienda = vivienda.id_vivienda
                #Arma el id de la imagen de tal forma que contenga IMG + los ultimos 7 digitos del id de la vivienda o menos
                imagen.id_imagen = 'IMG' + str(vivienda.id_vivienda)         
                vivienda.fecha_creacion = datetime.datetime.now(datetime.timezone.utc)
                vivienda.save()
                imagenQ = Imagen.query.filter_by(id_imagen=imagen.id_imagen).first()
                if imagenQ is None:
                    imagen.save()
    
    except Exception as e:
        return jsonify({'message': f'Error: {e}'})
    
    return jsonify({'message': f'Informacion de Portal Inmobiliario de {comunaConsulta} importada correctamente'})

