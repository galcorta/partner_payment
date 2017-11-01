#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests
from requests.auth import HTTPBasicAuth
from marshmallow import fields, Schema


"""
Tigo models
"""


class TigoMoneyManager:
    request_schema = None
    url_token = None
    url = None
    def __init__(self):
        self.request_schema = TigoMoneyRequestSchema()
        url_token = 'https://securesandbox.tigo.com/v1/oauth/mfs/payments/tokens'
        url = 'https://securesandbox.tigo.com/v2/tigo/mfs/payments'

    def TokenGeneration(self):
        response = requests.post(self.url_token, auth=HTTPBasicAuth('user', 'pass'))






class TigoMoneyRequestSchema(Schema):

    class MasterMerchant(Schema):
        account = fields.String
        pin = fields.String
        id = fields.String

    class Subscriber(Schema):
        account = fields.String
        country_code = fields.String
        country = fields.String
        email_id = fields.String

    class Payment(Schema):
        amount = fields.String
        currency_code = fields.String
        tax = fields.String
        fee = fields.String

    master_merchant = MasterMerchant
    subscriber = Subscriber
    payment = Payment
