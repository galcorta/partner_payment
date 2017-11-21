# -*- coding: utf-8 -*-

import shortuuid
from ...api import db
from marshmallow import fields, Schema
from .partner_debt import PartnerDebtSchema


# Models

class CollectionTransaction(db.Model):
    __tablename__ = "coltrx01"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    display_id = db.Column(db.String, nullable=False, unique=True, index=True, default=shortuuid.uuid)
    context_id = db.Column(db.Enum('partner_fee', 'product_sale', name='collection_transaction_context'))
    provider = db.Column(db.String)
    provider_voucher = db.Column(db.String)
    amount = db.Column(db.Integer)
    data = db.Column(db.Text)
    status = db.Column(db.String)
    write_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    create_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    active = db.Column(db.Boolean, default=True)

    def __init__(self, context_id, provider, amount, data, status):
        self.context_id = context_id
        self.provider = provider
        self.amount = amount
        self.data = data
        self.status = status

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


# Schemas
class CreateCollectionSchema(Schema):
    payment_method = fields.String()
    debts = fields.Nested(PartnerDebtSchema, many=True)
