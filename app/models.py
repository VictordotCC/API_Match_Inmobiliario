from sqlalchemy.dialects.postgresql import JSON
from app import db

from geoalchemy2 import Geometry
import datetime


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.String(10), primary_key=True)
    correo = db.Column(db.String(50), unique=True, nullable=False)
    clave = db.Column(db.String(128), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=True)
    activo = db.Column(db.Boolean, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    imagen = db.Column(db.String(100), nullable=True)
    links_contacto = db.Column(JSON, nullable=True)
    refresh_token = db.Column(db.String(500), nullable=True)
    refresh_token_expiry = db.Column(db.DateTime, nullable=True)

    idx_usuario_correo = db.Index('idx_usuario_correo', correo)

    def __repr__(self):
        return f'<Usuario {self.correo}>'
    
    def serialize(self):
        return {
            'id': self.id_usuario,
            'correo': self.correo,
            'tipo_usuario': self.tipo_usuario,
            'activo': self.activo,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'telefono': self.telefono,
            'fecha_creacion': self.fecha_creacion.strftime('%d-%m-%Y %H:%M:%S'),
            'imagen': self.imagen,
            'links_contacto': self.links_contacto
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Preferencia(db.Model):
    __tablename__ = 'preferencia'
    id_preferencia = db.Column(db.String(10), primary_key=True)
    area_total = db.Column(db.Float, nullable=True)
    pisos = db.Column(db.Integer, nullable=True)
    habitaciones = db.Column(db.Integer, nullable=True)
    tipo_valor = db.Column(db.String(10), nullable=True)
    precio_minimo = db.Column(db.Float, nullable=True)
    precio_maximo = db.Column(db.Float, nullable=True)
    estaciona = db.Column(db.Integer, nullable=True)
    bodega = db.Column(db.Integer, nullable=True)
    antiguedad = db.Column(db.Integer, nullable=True)
    tipo_vivienda = db.Column(db.Integer, nullable=True)
    condicion = db.Column(db.String(20), nullable=True)
    tipo_operacion = db.Column(db.Boolean, nullable=True)
    banos = db.Column(db.Integer, nullable=True)
    area_construida = db.Column(db.Float, nullable=True) 
    tipo_subsidio = db.Column(JSON, nullable=True)
    notificaciones = db.Column(db.Boolean, nullable=True)
    busqueda_automatica = db.Column(db.Boolean, nullable=True)
    distancia = db.Column(db.Float, nullable=True) 
    contactado = db.Column(db.Boolean, nullable=False, default=True)
    id_usuario = db.Column(db.String(10), db.ForeignKey('usuario.id_usuario'), nullable=False)

    idx_preferencia_id_usuario = db.Index('idx_preferencia_id_usuario', id_usuario)
    idx_preferencia_distancia = db.Index('idx_preferencia_distancia', distancia)

    def __repr__(self):
        return f'<Preferencia {self.id_preferencia}>'
    
    def serialize(self):
        return {
            'id': self.id_preferencia,
            'area_total': self.area_total,
            'pisos': self.pisos,
            'habitaciones': self.habitaciones,
            'tipo_valor': self.tipo_valor,
            'precio_minimo': self.precio_minimo,
            'precio_maximo': self.precio_maximo,
            'estaciona': self.estaciona,
            'bodega': self.bodega,
            'antiguedad': self.antiguedad,
            'tipo_vivienda': self.tipo_vivienda,
            'condicion': self.condicion,
            'tipo_operacion': self.tipo_operacion,
            'banos': self.banos,
            'area_construida': self.area_construida,
            'tipo_subsidio': self.tipo_subsidio,
            'notificaciones': self.notificaciones,
            'busqueda_automatica': self.busqueda_automatica,
            'distancia': self.distancia,
            'contactado': self.contactado,
            'id_usuario': self.id_usuario
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Region(db.Model):
    __tablename__ = 'region'
    id_region = db.Column(db.Integer, primary_key=True)
    nombre_region = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Region {self.nombre_region}>'
    
    def serialize(self):
        return {
            'id': self.id_region,
            'nombre': self.nombre_region
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Ciudad(db.Model):
    __tablename__ = 'ciudad'
    id_ciudad = db.Column(db.Integer, primary_key=True)
    nom_ciudad = db.Column(db.String(100), nullable=False)
    id_region = db.Column(db.Integer, db.ForeignKey('region.id_region'), nullable=False)

    def __repr__(self):
        return f'<Ciudad {self.nom_ciudad}>'
    
    def serialize(self):
        return {
            'id': self.id_ciudad,
            'nombre': self.nom_ciudad,
            'id_region': self.id_region
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Comuna(db.Model):
    __tablename__ = 'comuna'
    id_comuna = db.Column(db.Integer, primary_key=True)
    nom_comuna = db.Column(db.String(100), nullable=False)
    id_ciudad = db.Column(db.Integer, db.ForeignKey('ciudad.id_ciudad'), nullable=False)
    id_region = db.Column(db.Integer, db.ForeignKey('region.id_region'), nullable=False)

    def __repr__(self):
        return f'<Comuna {self.nom_comuna}>'
    
    def serialize(self):
        return {
            'id': self.id_comuna,
            'nombre': self.nom_comuna,
            'id_ciudad': self.id_ciudad
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Vecindario(db.Model):
    __tablename__ = 'vecindario'
    id_vecindario = db.Column(db.Integer, primary_key=True)
    nom_vecindario = db.Column(db.String(100), nullable=False)
    id_comuna = db.Column(db.Integer, db.ForeignKey('comuna.id_comuna'), nullable=False)
    id_ciudad = db.Column(db.Integer, db.ForeignKey('ciudad.id_ciudad'), nullable=False)
    id_region = db.Column(db.Integer, db.ForeignKey('region.id_region'), nullable=False)

    def __repr__(self):
        return f'<Vecindario {self.nom_vecindario}>'
    
    def serialize(self):
        return {
            'id': self.id_vecindario,
            'nombre': self.nom_vecindario,
            'id_comuna': self.id_comuna
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Vivienda(db.Model):
    __tablename__ = 'vivienda'
    id_vivienda = db.Column(db.String(50), primary_key=True)
    area_total = db.Column(db.Float, nullable=True)
    pisos = db.Column(db.Integer, nullable=True)
    habitaciones = db.Column(db.Integer, nullable=True)
    precio_uf = db.Column(db.Float, nullable=False)
    estaciona = db.Column(db.Integer, nullable=True)
    bodega = db.Column(db.Integer, nullable=True)
    antiguedad = db.Column(db.Integer, nullable=True)
    tipo_vivienda = db.Column(db.Integer, nullable=False) #0: Departamento, 1: Casa 2: Otro
    nombre_propiedad = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.String(500), nullable=False)
    condicion = db.Column(db.String(10), nullable=True)
    tipo_operacion = db.Column(db.Boolean, nullable=True) #0: Venta, 1: Arriendo
    banos = db.Column(db.Integer, nullable=True)
    area_construida = db.Column(db.Float, nullable=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    ubicacion = db.Column(Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFROMEWKT', name='geometry'), nullable=False) #Este campo es el resultado del calculo entre latitud y longitud
    tipo_subsidio = db.Column(db.String(15), nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    links_contacto = db.Column(JSON, nullable=True)
    id_vecindario = db.Column(db.Integer, db.ForeignKey('vecindario.id_vecindario'), nullable=True)
    id_comuna = db.Column(db.Integer, db.ForeignKey('comuna.id_comuna'), nullable=False)
    id_ciudad = db.Column(db.Integer, db.ForeignKey('ciudad.id_ciudad'), nullable=False)
    id_region = db.Column(db.Integer, db.ForeignKey('region.id_region'), nullable=False)
    id_usuario = db.Column(db.String(10), db.ForeignKey('usuario.id_usuario'), nullable=True)

    idx_vivienda_id_vecindario = db.Index('idx_vivienda_id_vecindario', id_vecindario)

    def __repr__(self):
        return f'<Vivienda {self.nombre_propiedad}>'
    
    def serialize(self):
        return {
            'id_vivienda': self.id_vivienda,
            'area_total': self.area_total,
            'pisos': self.pisos,
            'habitaciones': self.habitaciones,
            'precio_uf': self.precio_uf,
            'estaciona': self.estaciona,
            'bodega': self.bodega,
            'antiguedad': self.antiguedad,
            'tipo_vivienda': self.tipo_vivienda,
            'nombre_propiedad': self.nombre_propiedad,
            'descripcion': self.descripcion,
            'condicion': self.condicion,
            'tipo_operacion': self.tipo_operacion,
            'banos': self.banos,
            'area_construida': self.area_construida,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'tipo_subsidio': self.tipo_subsidio,
            'fecha_creacion': self.fecha_creacion.strftime('%d-%m-%Y %H:%M:%S'),
            'links_contacto': self.links_contacto,
            'id_vecindario': self.id_vecindario,
            'id_comuna': self.id_comuna,
            'id_ciudad': self.id_ciudad,
            'id_region': self.id_region
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Imagen(db.Model):
    __tablename__ = 'imagen'
    id_imagen = db.Column(db.String(50), primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    id_vivienda = db.Column(db.String(50), db.ForeignKey('vivienda.id_vivienda'), nullable=False)

    def __repr__(self):
        return f'<Imagen {self.id_imagen}>'
    
    def serialize(self):
        return {
            'id': self.id_imagen,
            'url': self.url,
            'id_vivienda': self.id_vivienda
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Favorito(db.Model):
    __tablename__ = 'favorito'
    id_favorito = db.Column(db.String(5), primary_key=True)
    fecha_guardado = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    id_usuario = db.Column(db.String(10), db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_vivienda = db.Column(db.String(50), db.ForeignKey('vivienda.id_vivienda'), nullable=False)

    idx_favorito_id_usuario = db.Index('idx_favorito_id_usuario', id_usuario)
    idx_favorito_id_vivienda = db.Index('idx_favorito_id_vivienda', id_vivienda)

    def __repr__(self):
        return f'<Favorito {self.id_favorito}>'
    
    def serialize(self):
        return {
            'id': self.id_favorito,
            'id_usuario': self.id_usuario,
            'fecha_guardado': self.fecha_guardado.strftime('%d-%m-%Y %H:%M:%S'),
            'id_vivienda': self.id_vivienda
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Match(db.Model):
    __tablename__ = 'match'
    id_match = db.Column(db.String(100), primary_key=True)
    fecha_coincidencia = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    visto = db.Column(db.Boolean, nullable=False, default=False)
    id_usuario = db.Column(db.String(10), db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_vivienda = db.Column(db.String(50), db.ForeignKey('vivienda.id_vivienda'), nullable=False)

    idx_match_id_usuario = db.Index('idx_match_id_usuario', id_usuario)
    idx_match_id_vivienda = db.Index('idx_match_id_vivienda', id_vivienda)
    
    def __repr__(self):
        return f'<Match {self.id_match}>'
    
    def serialize(self):
        return {
            'id': self.id_match,
            'id_usuario': self.id_usuario,
            'fecha_coincidencia': self.fecha_coincidencia.strftime('%d-%m-%Y %H:%M:%S'),
            'visto': self.visto,
            'id_vivienda': self.id_vivienda
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def bulk_save(matches):
        db.session.bulk_save_objects(matches)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
