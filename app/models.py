from sqlalchemy.dialects.postgresql import JSON
from app import db

import datetime


class User(db.Model):
    __tablename__ = 'user'
    id_user = db.Column(db.String(10), primary_key=True)
    correo = db.Column(db.String(50), unique=True, nullable=False)
    clave = db.Column(db.String(50), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=True)
    activo = db.Column(db.Boolean, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    imagen = db.Column(db.String(100), nullable=True)
    links_contacto = db.Column(JSON, nullable=True)

    idx_user_correo = db.Index('idx_user_correo', correo)

    def __repr__(self):
        return f'<User {self.correo}>'
    
    def serialize(self):
        return {
            'id': self.id_user,
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
    precio_uf = db.Column(db.Float, nullable=True)
    estaciona = db.Column(db.Integer, nullable=True)
    bodega = db.Column(db.Integer, nullable=True)
    antiguedad = db.Column(db.Integer, nullable=True)
    tipo_vivienda = db.Column(db.Integer, nullable=True)
    condicion = db.Column(db.String(20), nullable=True)
    tipo_operacion = db.Column(db.Boolean, nullable=True)
    banos = db.Column(db.Integer, nullable=True)
    area_construida = db.Column(db.Float, nullable=True)
    tipo_subsidio = db.Column(db.String(15), nullable=True)
    notificacion = db.Column(db.Boolean, nullable=True)
    busqueda_automatica = db.Column(db.Boolean, nullable=True)
    contactado = db.Column(db.Boolean, nullable=False, default=True)
    id_user = db.Column(db.String(10), db.ForeignKey('user.id_user'), nullable=False)

    idx_preferencia_id_user = db.Index('idx_preferencia_id_user', id_user)

    def __repr__(self):
        return f'<Preferencia {self.id_preferencia}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()





