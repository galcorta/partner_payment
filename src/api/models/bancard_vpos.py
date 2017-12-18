# -*- coding: utf-8 -*-

import hashlib
from marshmallow import fields, Schema

"""
Bancard vpos classes

"""

# Models

class Token(object):
    def __init__(self, private_key, shop_process_id, operation=None, amount=None, currency=None):
        self.private_key = private_key
        self.shop_process_id = shop_process_id
        self.operation = operation
        self.amount = amount
        self.currency = currency

    def __str__(self):
        hash_object = hashlib.md5(self.private_key + self.shop_process_id + (self.operation or '') +
                                  (self.amount or '') + (self.currency or ''))
        return hash_object.hexdigest()


class Operation(object):
    def __init__(self, token, shop_process_id, amount=None, currency=None, additional_data=None, description=None,
                 return_url=None, cancel_url=None, response=None, response_details=None, authorization_number=None):

        self.token = str(token)
        self.shop_process_id = shop_process_id
        self.amount = amount
        self.currency = currency
        self.additional_data = additional_data
        self.description = description
        self.return_url = return_url
        self.cancel_url = cancel_url
        self.response = response
        self.response_details = response_details
        self.authorization_number = authorization_number


class BaseRequest(object):
    def __init__(self, public_key, operation):
        self.public_key = public_key
        self.operation = operation

    def get_json(self):
        schema = BaseRequestSchema()
        data, errors = schema.dump(self)
        return data or None


# Schemas

class BaseOperationSchema(Schema):
    token = fields.Str()
    shop_process_id = fields.Str()
    amount = fields.Float()
    currency = fields.Str()
    additional_data = fields.Str()
    description = fields.Str()
    return_url = fields.Str()
    cancel_url = fields.Str()
    response = fields.Str()
    response_details = fields.Str()
    authorization_number = fields.Str()


class BaseRequestSchema(Schema):
    public_key = fields.String(required=True)
    operation = fields.Nested(BaseOperationSchema, required=True)
