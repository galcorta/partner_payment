#!/usr/bin/python
# -*- coding: utf-8 -*-

from ...api import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, Schema


class Debt(db.Model):
    __tablename__ = "ascup01"

    id_cuota = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_socio = db.Column(db.Integer, db.ForeignKey('assoc01.id_socio'), nullable=False)
    nro_socio = db.Column(db.Integer)
    categoria = db.Column(db.String(50))
    mes = db.Column(db.String(50))
    monto = db.Column(db.Integer)
    saldo_x_pagar = db.Column(db.Integer)
    amnistia = db.Column(db.String(50))
    vencimiento = db.Column(db.DateTime)
    pago = db.Column(db.DateTime)
    anno = db.Column(db.String(50))


    @property
    def id(self):
        return self.id_cuota

    def __init__(self, id_socio, mes, monto, saldo, vencimiento, pago, anno):
        self.id_socio = id_socio
        self.mes = mes
        self.monto = monto
        self.saldo_x_pagar = saldo
        self.vencimiento = vencimiento
        self.pago = pago
        self.anno = anno

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Debt {0}>'.format(str(self.id_cuota) + '/' + str(self.monto))


class DebtSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Debt
        sqla_session = db.session

# class DisplayDebtSchema(Schema):
#     period = fields.String()
#     debts = fields.Nested(DebtSchema, many=True)

