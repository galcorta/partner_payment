#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests, base64
from requests.auth import HTTPBasicAuth
from marshmallow import fields, Schema
from ..utils.config import DevelopmentConfig, ProductionConfig

"""
Tigo models
"""


class TigoMoneyManager:
    request_schema = None
    url_token = None
    url = None
    api_key = None
    secret = None

    def __init__(self):
        self.request_schema = TigoMoneyRequestSchema()
        self.url_token = DevelopmentConfig.TIGO_MONEY_TOKEN_URI
        self.url = DevelopmentConfig.TIGO_MONEY_PAYMENT_URI
        self.api_key = DevelopmentConfig.TIGO_MONEY_API_KEY
        self.secret = DevelopmentConfig.TIGO_MONEY_SECRET

    def _token_generation(self):
        usr_pass = self.api_key + ':' + self.secret
        b64_val = base64.b64encode(usr_pass)
        payload = 'grant_type=client_credentials'
        # response = requests.post(self.url_token, headers={"Authorization": "Basic %s" % b64_val}, data=payload)
        # response = requests.post(self.url_token, auth=HTTPBasicAuth('user', 'pass'))
        response = 'tigo-token-oauth'
        return response

    def payment_request(self, tm_request):
        access_token = self._token_generation()
        request = {
            'MasterMerchant':{
                '':
                '':
                '':
            }
        }




class MasterMerchant(Schema):
    account = fields.String()
    pin = fields.String()
    id = fields.String()


class Subscriber(Schema):
    account = fields.String()
    country_code = fields.String()
    country = fields.String()
    email_id = fields.String()


class Payment(Schema):
    amount = fields.String()
    currency_code = fields.String()
    tax = fields.String()
    fee = fields.String()


class TigoMoneyRequestSchema(Schema):
    master_merchant = fields.Nested(MasterMerchant)
    subscriber = fields.Nested(Subscriber)
    payment = fields.Nested(Payment)
