import json
import uuid
import datetime

from flask import Blueprint, jsonify, request, url_for, render_template
from flask_cors import CORS, cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from geoalchemy2 import Geography
from geoalchemy2 import functions as func

from sqlalchemy import func as sqlfunc
from sqlalchemy import between, or_
from sqlalchemy.orm import joinedload

from app.models import *
from app.helpers import refreshtoken, fillDB_PI
from app.helpers import leer_georef
from app.helpers import aes
from app.helpers import auth
from app.helpers.email import send_email
from config import distance_bleed

app = Blueprint('main', __name__)
#CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

@app.after_request
def afer_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

@app.route('/')
def index():
    return jsonify({'message': 'API Match Inmobiliario V1.0'})

#RUTAS DE USUARIO

@app.route('/usuario', methods=['GET'])
def usuario():
    correo = request.args.get('usuario')
    usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario is not None:
        return jsonify(usuario.correo)
    else:
        return jsonify({'message': 'Usuario no encontrado'})

@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    usuario = Usuario()
    usuario.correo = data['correo']
    usuario.nombres = data['nombres']
    usuario.apellidos = data['apellidos']
    usuario.telefono = data['telefono']
    usuario.fecha_creacion = datetime.datetime.now(datetime.timezone.utc)
    usuario.activo = False
    cantidad_usuarios = Usuario.query.count()
    hexa = format(cantidad_usuarios, 'X')
    usuario.id_usuario = 'miU#' + hexa.zfill(6)
    clave = data['contrasena']
    usuario.clave = aes.encrypt(clave)
    token = auth.generate_confirmation_token(usuario.correo)
    confirm_url = url_for('main.confirmar', token=token, _external=True)
    html = render_template('confirm_email.html', confirm_url=confirm_url)
    subject = 'Por favor confirma tu correo'
    send_email(usuario.correo, subject, html)
    usuario.save()
    #Crear preferencias
    preferencias = Preferencia()
    preferencias.id_usuario = usuario.id_usuario
    hash = aes.encrypt(preferencias.id_usuario)
    preferencias.id_preferencia = 'MIPF' + hash[0:6]
    preferencias.save()
    return jsonify({'message': 'Usuario registrado'})

@app.route('/dar-alta', methods=['GET'])
def dar_alta():
    correo = request.args.get('correo')
    usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario is not None:
        token = auth.generate_confirmation_token(usuario.correo)
        confirm_url = url_for('main.confirmar', token=token, _external=True)
        html = render_template('dar_alta.html', confirm_url=confirm_url)
        subject = 'Confirma la recuperación de tu cuenta'
        send_email(usuario.correo, subject, html)
        return jsonify({'message': 'Correo de confirmación enviado'})
    return jsonify({'message': 'Usuario no encontrado'})

@app.route('/dar-baja', methods=['GET'])
def dar_baja():
    correo = request.args.get('correo')
    usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario is not None:
        usuario.activo = False
        usuario.update()
        return jsonify({'message': 'Usuario dado de baja'})

@app.route('/confirmar/<token>', methods=['GET'])
def confirmar(token):
    email = auth.confirm_token(token)
    if email:
        usuario = Usuario.query.filter_by(correo=email).first()
        if usuario is not None:
            usuario.activo = True
            usuario.update()
            return jsonify({'message': 'Usuario confirmado'})
    return jsonify({'message': 'Usuario no encontrado'})

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'GET':
        correo = request.args.get('correo')
        usuario = Usuario.query.filter_by(correo=correo).first()
        print(usuario)
        if usuario is not None:
            token = auth.generate_reset_token(correo)
            html = render_template('reset_email.html', token=token)
            subject = 'Recuperación de contraseña'
            send_email(correo, subject, html)
            return jsonify({'message': 'Correo enviado', 'status': 200}), 200
        else:
            return jsonify({'message': 'Usuario no encontrado', 'status': 404}), 404
    elif request.method == 'POST':
        data = request.get_json()
        correo = data['correo']
        clave = data['contrasena']
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario:
            usuario.clave = aes.encrypt(clave)
            usuario.update()
            return jsonify({'message': 'Contraseña actualizada', 'status': 200}), 200
        else:
            return jsonify({'message': 'Usuario no encontrado', 'status': 404}), 404

@app.route('/verificar_recuperacion', methods=['GET'])
def verificar_recuperacion():
    token = request.args.get('token')
    correo = request.args.get('correo')
    email = auth.verify_reset_token(token)
    if email == correo:
        return jsonify({'message': 'Token válido', 'status':200}), 200
    else:
        return jsonify({'message': 'Token inválido'}), 401

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo = data['correo']
    clave = data['contrasena']
    clave_aes = aes.encrypt(clave)
    #usuario = Usuario.query.filter_by(correo=correo, clave=clave).first()
    usuario = Usuario.query.filter_by(correo=correo, clave=clave_aes).first()
    if usuario:
        if not usuario.activo:
            return jsonify({'message': 'Usuario no confirmado', 'status': 401, 'activo': usuario.activo})
        access_token, refresh_token = auth.create_tokens(usuario.id_usuario)
        expiry = datetime.datetime.fromtimestamp(auth.decode_token(refresh_token)['exp'], datetime.timezone.utc)
        usuario.refresh_token = refresh_token
        usuario.refresh_token_expiry = expiry
        usuario.update()
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': usuario.serialize(),
            'status': 200
        }), 200
    return jsonify({'message': 'Usuario o contraseña incorrectos', 'status':401})

#RUTAS DE FUNCIONALIDAD

@app.route('/auto-login', methods=['POST'])
def auto_login():
    try:
    # Verificar si hay un access token válido
        if verify_jwt_in_request():
            current_user = get_jwt_identity()
            print(current_user)
            usuario = Usuario.query.filter_by(id_usuario=current_user).first()
            if usuario:
                # El access token es válido y devuelve el usuario
                return jsonify({
                    'access_token': request.headers.get('Authorization').split(' ')[1],
                    'user':     usuario.serialize(),
                    'status': 200
                    }), 200
    except Exception as e:
        # Si no hay un access token válido, verificar el refresh token
        refresh_token = request.get_json().get('refresh_token')
        if not refresh_token:
            # No hay token de refresco, el usuario debe loguear
            return jsonify({'message': 'No hay tokens válidos'}), 401

        data = auth.decode_token(refresh_token)
        if not data:
            # Error al decodificar el token de refresco, el usuario debe loguear
            return jsonify({'message': 'Token inválido'}), 401

        user_id = data['sub']
        usuario = Usuario.query.filter_by(id_usuario=user_id, refresh_token=refresh_token).first()
        if not usuario:
            # Hay token de refresco pero el usuario no existe, el usuario debe loguear
            return jsonify({'message': 'Refresh Token inválido'}), 401
        # Token de acceso expirado, se genera uno nuevo, el usuario no necesita loguear
        new_access_token = auth.new_access_token(user_id)
        return jsonify({
            'access_token': new_access_token,
            'user': usuario.serialize(),
            'status': 200
        }), 200

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_jwt_token():
    current_user = get_jwt_identity()
    usuario = Usuario.query.filter_by(id_usuario=current_user).first()
    if not usuario:
        #Usuario no encontrado, el usuario debe loguear
        return jsonify({'message': 'Usuario no encontrado'}), 401
    print(usuario.refresh_token)
    if auth.verify_expiry(usuario.refresh_token):
        #Token de refresco expirado, el usuario debe loguear
        return jsonify({'message': 'Token expirado'}), 401
    new_access_token, new_refresh_token = auth.create_tokens(usuario.id_usuario)
    usuario.refresh_token = new_refresh_token
    usuario.update()
    return jsonify({'access_token': new_access_token, 'refresh_token': new_refresh_token}), 200

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
@jwt_required()
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
        referencia = f'SRID=4326;POINT({data["ubicacion"]["lon"]} {data["ubicacion"]["lat"]})'
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
        
        subsidios = data['preferencias']['tipo_subsidio'] # obtiene listado de subsidios
        if subsidios:
            condiciones = [Vivienda.tipo_subsidio.contains(subsidio) for subsidio in subsidios]
            query = query.filter(or_(*condiciones))

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
@jwt_required()
def viviendas_cercanas():
    latitud = request.args.get('lat')
    longitud = request.args.get('lon')
    #page = int(request.args.get('page', 1)) PAGINACION YA NO ES NECESARIA
    #per_page = int(request.args.get('per_page', 100))
    distancia = 1000
    referencia = f'SRID=4326;POINT({longitud} {latitud})'

    #offset = (page - 1) * per_page

    viviendas = db.session.query(
        Vivienda,
        Imagen,
        func.ST_Distance(
            sqlfunc.cast(Vivienda.ubicacion, Geography),
            sqlfunc.cast(func.ST_GeographyFromText(referencia), Geography)
            ).label('cercania')
        ).join(Imagen, Imagen.id_vivienda == Vivienda.id_vivienda).filter(
            func.ST_DWithin(
                sqlfunc.cast(Vivienda.ubicacion, Geography),
                sqlfunc.cast(func.ST_GeographyFromText(referencia), Geography),
                distancia
                )
        ).order_by('cercania').limit(20).all()
        
    viviendas_serializadas = [{**vivienda.serialize(), 'imagenes': [imagen.serialize()], 'cercania': cercania} for vivienda, imagen, cercania in viviendas]
    return jsonify(viviendas_serializadas)

@app.route('/get_matches', methods=['GET'])
@jwt_required()
def get_matches():
    usuario = request.args.get('usuario')
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    usuario_id = Usuario.query.filter_by(correo=usuario).first().id_usuario
    if usuario_id is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    referencia = f'SRID=4326;POINT({lon} {lat})'

    matches = (
        db.session.query(
            Match,
            Vivienda,
            func.ST_Distance(
                func.ST_GeographyFromText(referencia),
                sqlfunc.cast(Vivienda.ubicacion, Geography)
            ).label('cercania')
        )
        .join(Vivienda, Match.id_vivienda == Vivienda.id_vivienda)
        .filter(Match.id_usuario == usuario_id, Match.visto == False)
        .order_by(Match.fecha_coincidencia.desc())
        .limit(20)
        .all()
    )
    """
    matches = Match.query.filter(
        Match.id_usuario == usuario_id,
        Match.visto == False).order_by(Match.fecha_coincidencia.desc()
        ).limit(20).all()
    """
    viviendas_ids = [match.id_vivienda for match, vivienda, cercania in matches]
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
            'id_match': match.id_match,
            'cercania': int(cercania)
        } for match, vivienda, cercania in matches if match.id_vivienda in viviendas_dict
    ]
    return jsonify(viviendas)

@app.route('/marcar_visto', methods=['GET'])
@jwt_required()
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

@app.route('/favoritos', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def favoritos():
    try:
        if request.method == 'GET':
            correo = request.args.get('usuario')
            lat = request.args.get('lat')
            lon = request.args.get('lon')
            usuario = Usuario.query.filter_by(correo=correo).first()
            if usuario is None:
                if usuario is None:
                    return jsonify({'message': f'Usuario no encontrado para el correo: {correo}'})
                
            favoritos = db.session.query(
                Favorito,
                Vivienda,
                Imagen,
                func.ST_Distance(
                    sqlfunc.cast(Vivienda.ubicacion, Geography),
                    sqlfunc.cast(func.ST_GeographyFromText(f'SRID=4326;POINT({lon} {lat})'), Geography)
                ).label('cercania')
            ).filter(Favorito.id_usuario == usuario.id_usuario
            ).join(Vivienda, Favorito.id_vivienda == Vivienda.id_vivienda
            ).join(Imagen, Imagen.id_vivienda == Vivienda.id_vivienda
            ).filter(Favorito.id_usuario == usuario.id_usuario
            ).order_by(Favorito.fecha_guardado.desc()).all()

            toreturn = []

            for fav, vivienda, imagen, cercania in favoritos:
                toreturn.append({
                    **vivienda.serialize(),
                    'imagenes': [imagen.serialize()],
                    'cercania': cercania,
                    'id_favorito': fav.id_favorito,
                    'fecha_guardado': datetime.datetime.strftime(fav.fecha_guardado, '%d-%m-%Y %H:%M:%S')
                })
            return jsonify(toreturn), 200
        elif request.method == 'POST':
            fav = Favorito()
            data = request.get_json()
            usuario = data['usuario']
            fav.id_usuario = Usuario.query.filter_by(correo=usuario).first().id_usuario
            fav.id_vivienda = data['id_vivienda']
            fav.fecha_guardado = datetime.datetime.now(datetime.timezone.utc)
            #get last fav id
            last_fav = Favorito.query.order_by(Favorito.id_favorito.desc()).first()
            if last_fav is None:
                fav.id_favorito = fav.id_usuario[0:2] + str(1).zfill(3)
            else:
                fav.id_favorito = fav.id_usuario[0:2] + str(int(last_fav.id_favorito[2:]) + 1).zfill(3)
            existe = Favorito.query.filter_by(id_usuario=fav.id_usuario, id_vivienda=fav.id_vivienda).first()
            if existe is not None:
                return jsonify({'message': 'Vivienda ya en favoritos'}), 400
            id_repetido = Favorito.query.filter_by(id_favorito=fav.id_favorito).first()
            if id_repetido is not None:
                fav.id_favorito = fav.id_usuario[0:2] + str(int(id_repetido.id_favorito[2:]) + 1).zfill(3)
            fav.save()
            return jsonify({'message': 'Vivienda agregada a favoritos'}, 200) 
        elif request.method == 'DELETE':
            data = request.get_json()
            correo = data['usuario']
            id_vivienda = data['id_vivienda']
            usuario = Usuario.query.filter_by(correo=correo).first()
            favorito = Favorito.query.filter(
                Favorito.id_usuario == usuario.id_usuario,
                Favorito.id_vivienda == id_vivienda
            ).first()
            if favorito is not None:
                favorito.delete()
                return jsonify({'message': 'Vivienda eliminada de favoritos'})
            else:
                return jsonify({'message': 'Vivienda no encontrada en favoritos'})
    except Exception as e:
        return jsonify({'message': 'Error al agregar favorito', 'EXC': str(e)}, 500)

#RUTAS CRUD

@app.route('/preferencia', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def preferencia():
    if request.method == 'GET':
        correo = request.args.get('correo')
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario is None:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        preferencias = Preferencia.query.filter_by(id_usuario=usuario.id_usuario).first()
        if preferencias is not None:
            return jsonify({
                'preferencias': preferencias.serialize(),
                'status': 200})
        else:
            return jsonify({'message': 'Preferencia no encontrada'}), 404
    elif request.method == 'POST':
        data = request.get_json()
        usuario = Usuario.query.filter_by(correo=data['correo']).first()
        if usuario is None:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        preferencias = Preferencia.query.filter_by(id_usuario=usuario.id_usuario).first()
        if preferencias is not None:
            #Update preferencia
            for key, value in data['preferencias'].items():
                if key == 'usuario':
                    continue
                setattr(preferencias, key, value)
            preferencias.update()
            #Borrar todos los match del usuario
            print(usuario.id_usuario)
            Match.query.filter_by(id_usuario=usuario.id_usuario).delete()
            db.session.commit()
            return jsonify({'message': 'Preferencias actualizadas', 'status':200})
        elif preferencias is None:
            preferencias = Preferencia()
            preferencias.id_usuario = usuario.id_usuario
            hash = aes.encrypt(preferencias.id_usuario)
            preferencias.id_preferencia = 'MIPF' + hash[0:6]
            for key, value in data['preferencias'].items():
                if key == 'usuario':
                    continue
                setattr(preferencias, key, value)
            preferencias.save()
        return jsonify({'message': 'Preferencias guardadas', 'status':200})

@app.route('/imagenes', methods=['GET','POST'])
@jwt_required()
def imagenes():
    if request.method == 'GET':
        id_vivienda = request.args.get('id_vivienda')
        imagenes = Imagen.query.filter_by(id_vivienda=id_vivienda).all()
        if imagenes is not None:
            return jsonify([imagen.serialize() for imagen in imagenes])
        else:
            return jsonify({'message': 'Imagenes no encontradas'})
    elif request.method == 'POST':
        data = request.get_json()
        id_vivienda = data['id_vivienda']
        for img in data['imagenes']:
            count = Imagen.query.count()    
            imagen = Imagen()
            imagen.id_vivienda = id_vivienda
            imagen.url = str(img)
            hex = format(count, 'X').zfill(6)
            unique_part = str(uuid.uuid4()).replace('-', '')[:8]
            timestamp = int(datetime.datetime.now().timestamp())
            imagen.id_imagen = f'IMG{imagen.id_vivienda[2:10]}{timestamp}{hex}{unique_part}'
            imagen.save()
        return jsonify({'message': 'Imagen guardada'})
    
#RUTAS DE VENDEDOR

@app.route('/v_viviendas', methods=['GET', 'POST'])
@jwt_required()
def v_viviendas():
    if request.method == 'GET':
        correo = request.args.get('correo')
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario is not None:
            viviendas = Vivienda.query.filter_by(id_usuario=usuario.id_usuario).all()
            if viviendas is not None:
                return jsonify([vivienda.serialize() for vivienda in viviendas])
            else:
                return jsonify({'message': 'Viviendas no encontradas'})
        else:
            return jsonify({'message': 'Usuario no encontrado'})
    elif request.method == 'POST':
        #Guardar Vivienda
        data = request.get_json()['vivienda']
        vivienda = Vivienda()
        #Genera el id de la vivienda
        cantidad_viviendas = Vivienda.query.count()
        hexa = format(cantidad_viviendas, 'X').zfill(6)
        unique_part = str(uuid.uuid4()).replace('-', '')[:8]
        timestamp = int(datetime.datetime.now().timestamp())
        id_vivienda = f'MI{unique_part}{timestamp}{hexa}'
        vivienda.id_vivienda = id_vivienda[:50]
        #Resto de Propiedades
        vivienda.area_total = data['area_total'] 
        vivienda.pisos = data['pisos']
        vivienda.habitaciones = data['habitaciones']
        vivienda.precio_uf = data['precio_uf']
        vivienda.estaciona = data['estaciona']
        vivienda.bodega = data['bodega']
        vivienda.antiguedad = data['antiguedad']
        vivienda.tipo_vivienda = data['tipo_vivienda']
        vivienda.nombre_propiedad = data['nombre_propiedad']
        vivienda.descripcion = data['descripcion']
        vivienda.condicion = data['condicion']
        vivienda.tipo_operacion = data['tipo_operacion']
        vivienda.banos = data['banos']
        vivienda.area_construida = data['area_construida']
        vivienda.latitud = data['latitud']
        vivienda.longitud = data['longitud']
        vivienda.ubicacion = func.ST_GeomFromText(f'POINT({vivienda.longitud} {vivienda.latitud})', 4326)
        vivienda.tipo_subsidio = data['tipo_subsidio']
        vivienda.fecha_creacion = datetime.datetime.now(datetime.timezone.utc)
        vivienda.links_contacto = json.dumps(data['links_contacto'])
        #TODO: Obtener vecindario
        geodata = leer_georef.leer_georef(vivienda.latitud, vivienda.longitud)
        if geodata is None:
            return jsonify({'message': 'Error al obtener geodata'})
        id_comuna = Comuna.query.filter_by(nom_comuna=geodata['comuna']).first().id_comuna
        id_ciudad = Ciudad.query.filter_by(nom_ciudad=geodata['ciudad']).first().id_ciudad
        id_region = Region.query.filter_by(nombre_region=geodata['region']).first().id_region
        vivienda.id_comuna = id_comuna
        vivienda.id_ciudad = id_ciudad
        vivienda.id_region = id_region
        vivienda.id_usuario = Usuario.query.filter_by(correo=data['correo']).first().id_usuario
        vivienda.save()
        return jsonify({'message': 'Vivienda guardada', 'id_vivienda': vivienda.id_vivienda})

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

