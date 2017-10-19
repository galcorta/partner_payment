#!/usr/bin/python
# -*- coding: utf-8 -*-

from ...api import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, Schema


class Collection(db.Model):
    __tablename__ = "ascob01"

    id_cobro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_socio = db.Column(db.Integer, db.ForeignKey('assoc01.id_socio'), nullable=False)
    fecha = db.Column(db.Date)
    anno = db.Column(db.Integer)
    nro_socio = db.Column(db.Integer)
    monto_a_cobrar = db.Column(db.String(50))
    cantidad_de_cuotas = db.Column(db.Integer)
    forma_de_pago = db.Column(db.String(50))  # Efectivo, Cheque, Tarjeta, OnLine
    efectivo = db.Column(db.Integer)
    nro_transaccion = db.Column(db.Integer)
    monto_anual_a_cobrar = db.Column(db.Integer)
    categoria = db.Column(db.String(50))
    vuelto = db.Column(db.Integer)
    corresponde_a = db.Column(db.String(50))
    cuotas_afectadas = db.Column(db.Text)
    nota = db.Column(db.String(50))
    comprobante = db.Column(db.String(255))
    medio_pago_id = db.Column(db.Integer, db.ForeignKey('asmepag01.id_medio_pago'))

    @property
    def id(self):
        return self.id_cobro

    def __init__(self, id_socio, efectivo, fecha, forma_de_pago, nro_socio=None , cantidad_de_cuotas=None,
                 cuotas_afectadas=None, comprobante=None, medio_pago_id=None):
        self.id_socio = id_socio
        self.efectivo = efectivo
        self.fecha = fecha
        self.forma_de_pago = forma_de_pago
        self.nro_socio = nro_socio
        self.cantidad_de_cuotas = cantidad_de_cuotas
        self.cuotas_afectadas = cuotas_afectadas
        self.comprobante = comprobante
        self.medio_pago_id = medio_pago_id

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Collection {0}>'.format(self.efectivo)


# class CreateCollectionSchema(Schema):




