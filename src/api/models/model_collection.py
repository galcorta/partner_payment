#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from ...api import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, Schema
from .model_debt import DebtSchema


class Collection(db.Model):
    __tablename__ = "ascob01"

    id_cobro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_socio = db.Column(db.Integer, db.ForeignKey('assoc01.id_socio'), nullable=False)
    fecha = db.Column(db.Date)
    nro_socio = db.Column(db.Integer)
    categoria = db.Column(db.String(50))
    anno = db.Column(db.Integer)
    monto_cobrado = db.Column(db.Integer)
    nro_recibo = db.Column(db.Integer)
    estado = db.Column(db.Text)
    nota = db.Column(db.Text)
    details = db.relationship('CollectionDetail', backref='collection',
                                lazy='dynamic')
    collection_ways = db.relationship('CollectionWay', backref='collection',
                                lazy='dynamic')

    @property
    def id(self):
        return self.id_cobro

    def __init__(self, id_socio, fecha, nro_socio, categoria, anno, monto_cobrado, nro_recibo, estado, nota,
                 details, collection_ways):
        self.id_socio = id_socio
        self.fecha = fecha
        self.nro_socio = nro_socio
        self.categoria = categoria
        self.anno = anno
        self.monto_cobrado = monto_cobrado
        self.nro_recibo = nro_recibo
        self.estado = estado
        self.nota = nota
        self.details = details
        self.collection_ways=collection_ways

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Collection {0}>'.format(self.efectivo)


class CollectionDetail(db.Model):
    __tablename__ = "ascbd01"

    id_cobro_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cobro = db.Column(db.Integer, db.ForeignKey('ascob01.id_cobro'), nullable=False)
    id_cuota = db.Column(db.Integer)
    monto = db.Column(db.Integer)
    fecha = db.Column(db.Date)

    @property
    def id(self):
        return self.id_cobro_detalle

    def __init__(self, id_cuota, monto, fecha):
        self.id_cuota = id_cuota
        self.monto = monto
        self.fecha = fecha


class CollectionWay(db.Model):
    __tablename__ = "astpc01"

    id_tipo_cobro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cobro = db.Column(db.Integer, db.ForeignKey('ascob01.id_cobro'), nullable=False)
    id_socio = db.Column(db.Integer)
    nro_socio = db.Column(db.Integer)
    fecha = db.Column(db.Date)
    tipo = db.Column(db.String(50))
    monto = db.Column(db.Integer)

    @property
    def id(self):
        return self.id_tipo_cobro

    def __init__(self, id_socio, nro_socio, fecha, tipo, monto):
        self.id_socio = id_socio
        self.nro_socio = nro_socio
        self.fecha = fecha
        self.tipo = tipo,
        self.monto = monto

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<CollectionWay {0}>'.format(self.id_tipo_cobro)


class CollectionRequest(db.Model):
    __tablename__ = "asppreq01"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_socio = db.Column(db.Integer)
    payment_provider = db.Column(db.String)
    total_amount = db.Column(db.String)
    message = db.Column(db.Text)
    status = db.Column(db.String)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, id_socio, payment_provider, amount, message, status):
        self.id_socio = id_socio
        self.payment_provider = payment_provider
        self.amount = amount
        self.message = message
        self.status = status



class CreateCollectionSchema(Schema):
    payment_method = fields.String()
    debts = fields.Nested(DebtSchema, many=True)

