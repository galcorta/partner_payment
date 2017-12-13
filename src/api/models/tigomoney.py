# -*- coding: utf-8 -*-

from marshmallow import fields, Schema

"""
Tigo money classes

"""


# Schemas
class MasterMerchant(Schema):
    account = fields.String()
    pin = fields.String()
    id = fields.String()


class Subscriber(Schema):
    account = fields.String()
    countryCode = fields.String()
    country = fields.String()
    emailId = fields.String()


class OriginPayment(Schema):
    amount = fields.String()
    currencyCode = fields.String()
    tax = fields.String()
    fee = fields.String()


class LocalPayment(Schema):
    amount = fields.String()
    currencyCode = fields.String()


class TigoMoneyRequestSchema(Schema):
    Subscriber = fields.Nested(Subscriber(), required=True)
    OriginPayment = fields.Nested(OriginPayment(), required=True)
    language = fields.String(missing='spa')
    exchangeRate = fields.String(missing='1')
    MasterMerchant = fields.Nested(MasterMerchant())
    merchantTransactionId = fields.String()
    LocalPayment = fields.Nested(LocalPayment())
    redirectUri = fields.String()
    callbackUri = fields.String()


class TokenGenerationResponseSchema(Schema):
    tokenType = fields.String()
    accessToken = fields.String()
    issuedAt = fields.String()
    expiresIn = fields.String()
