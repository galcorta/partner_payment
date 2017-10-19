#!/usr/bin/python
# -*- coding: utf-8 -*-

from ...api import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


class MedioPago(db.Model):
    __tablename__ = "asmepag01"

    id_medio_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)

    @property
    def id(self):
        return self.id_medio_pago

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<MedioPago {0}>'.format(self.nombre)
