#!/usr/bin/python
# -*- coding: utf-8 -*-

from ...api import app, db, bcrypt
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, Schema


class Partner(db.Model):
    __tablename__ = 'assoc01'

    # id_socio = db.Column(db.Integer, db.Sequence('assoc01_seq', start=1, increment=1), primary_key=True)
    id_socio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nro_socio = db.Column(db.Integer)
    fecha_ingreso = db.Column(db.Date)
    empresa = db.Column(db.Text)
    nombre = db.Column(db.String(255))
    categoria = db.Column(db.String(255))
    estado = db.Column(db.String(255))
    documento_identidad = db.Column(db.String(255))
    identidad = db.Column(db.String(255))
    sexo = db.Column(db.String(255))
    estado_civil = db.Column(db.String(255))
    fecha_nacimiento = db.Column(db.DateTime)
    edad_actual = db.Column(db.String(255))
    direccion = db.Column(db.String(255))
    departamento = db.Column(db.String(255))
    ciudad = db.Column(db.String(255))
    barrio = db.Column(db.String(255))
    direccion_laboral = db.Column(db.String(255))
    telefono = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    celular = db.Column(db.String(255))
    foto_socio = db.Column(db.String(255))
    comentario = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)

    @property
    def id(self):
        return self.id_socio

    def __init__(self, nro_socio, nombre, documento_identidad, email, password):
        self.nro_socio = nro_socio
        self.nombre = nombre
        self.documento_identidad = documento_identidad
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode('utf-8')

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Partner {0}>'.format(self.email)
    


class PartnerSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Partner
        sqla_session = db.session


class PartnerLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class PartnerLoginResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    token = fields.String()
