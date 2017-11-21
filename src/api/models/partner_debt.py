#!/usr/bin/python
# -*- coding: utf-8 -*-

from ...api import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


class PartnerDebt(db.Model):
    __tablename__ = "ascuo01"

    id = db.Column('id_cuota', db.Integer, primary_key=True, autoincrement=True)
    id_socio = db.Column(db.Integer, db.ForeignKey('assoc01.id_socio'), nullable=False)
    nro_socio = db.Column(db.Integer)
    categoria = db.Column(db.String(50))
    monto_cobrado = db.Column(db.Integer)
    saldo_x_cobrar = db.Column(db.Integer)
    amnistia = db.Column(db.String(50))
    vencimiento = db.Column(db.Date)
    anio = db.Column(db.Integer)
    mes = db.Column(db.String(50))

    def __init__(self, id_socio, mes, monto, saldo, vencimiento, anio):
        self.id_socio = id_socio
        self.mes = mes
        self.monto_cobrado = monto
        self.saldo_x_cobrar = saldo
        self.vencimiento = vencimiento
        self.anio = anio

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Debt {0}>'.format(str(self.id) + '/' + str(self.saldo_x_cobrar))


class PartnerDebtSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = PartnerDebt
        sqla_session = db.session

    amount = fields.Integer()
