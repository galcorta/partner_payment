# -*- coding: utf-8 -*-

from marshmallow import fields, Schema


class RedCobranzaRequestSchema(Schema):
    name = fields.String()
    voucher = fields.String()
