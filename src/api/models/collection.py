# -*- coding: utf-8 -*-

import json
import logging
import random
import time
import shortuuid
from ...api import db
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import ModelSchema
from ..models.factusys import PartnerCollection, PartnerDebtSchema
from ..models.payment_provider import PaymentProvider
from ...api import app, db, bcrypt
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


# Models
def default_display_id():
    return int(time.time() + random.getrandbits(32))


class CollectionTransaction(db.Model):
    __tablename__ = "CollectionTransaction"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # display_id = db.Column(db.String(25), nullable=False, unique=True, index=True, default=shortuuid.uuid)
    display_id = db.Column(db.Integer)
    context_id = db.Column(db.Enum('partner_fee', 'product_sale', name='collection_transaction_context'))
    collection_entity_id = db.Column(db.Integer, db.ForeignKey('CollectionEntity.id'), nullable=False)
    payment_provider_id = db.Column(db.Integer, db.ForeignKey('PaymentProvider.id'))
    payment_provider_voucher = db.Column(db.String(50))
    amount = db.Column(db.Float)
    data = db.Column(db.Text)
    status = db.Column(db.String(15))
    write_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    create_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    partner_id = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)

    payment_provider = db.relationship("PaymentProvider")

    def create(self):
        db.session.add(self)
        db.session.commit()
        self.display_id = int(time.time() + self.id)
        db.session.commit()
        return self


class CollectionEntity(db.Model):
    __tablename__ = "CollectionEntity"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    write_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    create_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    active = db.Column(db.Boolean, default=True)

    def hash_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def verify_password(self, password):
        return bcrypt.check_password_hash(
            self.password_hash, password
        )

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    # def update(self):
    #     db.session.(self)
    #     db.session.commit()
    #     return self

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)

        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        entity = CollectionEntity.query.get(data['id'])
        return entity


# Schemas
class CreateCollectionSchema(Schema):
    payment_method = fields.Str()
    debts = fields.Nested(PartnerDebtSchema, many=True)


class CollectionEntitySchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = CollectionEntity
        sqla_session = db.session


class CollectionTransactionSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = CollectionTransaction
        sqla_session = db.session
