# -*- coding: utf-8 -*-

import requests, json
from marshmallow import fields, Schema
from .payment_provider import PaymentProvider, PaymentProviderOperation
from .collection import CollectionTransaction
from .partner_debt import PartnerDebtSchema
from .partner import PartnerCollection, PartnerCollectionWay
from requests.auth import HTTPBasicAuth
from ...api import db
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


# Controllers
class TigoMoneyManager:

    def __init__(self):
        self.request_schema = TigoMoneyRequestSchema()
        self.payment_provider = PaymentProvider.query.filter_by(name='tigo_money').one()
        self.token_uri = self.payment_provider.get_endpoint_by_name('TM_TOKEN_URI')
        self.payment_url = self.payment_provider.get_endpoint_by_name('TM_PAYMENT_URI')
        self.api_key = self.payment_provider.get_config_by_name('TM_API_KEY')
        self.secret = self.payment_provider.get_config_by_name('TM_SECRET')
        self.redirect_uri = self.payment_provider.get_config_by_name('TM_REDIRECT_URI')
        self.callback_uri = self.payment_provider.get_config_by_name('TM_CALLBACK_URI')

    def _token_generation(self):
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        auth = HTTPBasicAuth(self.api_key, self.secret)
        payload = 'grant_type=client_credentials'
        response = requests.post(self.token_uri, auth=auth, headers=headers, data=payload)
        if response.status_code == requests.codes.ok:
            resp_json = response.json()
            return resp_json['accessToken']
        else:
            return None

    def _request_treatment(self, collection):
        request, error = self.request_schema.load(json.loads(collection.data)['payment_provider_data'])
        if not error:
            request['merchantTransactionId'] = collection.display_id
            request['MasterMerchant'] = {
                'account': self.payment_provider.get_config_by_name('TM_AGENT_MSISDN'),
                'pin': self.payment_provider.get_config_by_name('TM_AGENT_PIN'),
                'id': 'Club Olimpia'
            }
            request['LocalPayment'] = {
                'amount': request['OriginPayment']['amount'],
                'currencyCode': request['OriginPayment']['currencyCode']
            }
            request['redirectUri'] = self.redirect_uri
            request['callbackUri'] = self.callback_uri
            return self.request_schema.dump(request)
        else:
            return None, True
    # def _response_treatment(self, response):
    #     if response.status_code == 400:
    #         pass

    def payment_request(self, collection):
        req_dump, error = self._request_treatment(collection)
        if not error:
            access_token = self._token_generation()
            if access_token:
                    tm_req = PaymentProviderOperation(transaction_id=collection.id,
                                                      payment_provider_id=self.payment_provider.id,
                                                      operation_type='request',
                                                      direction='sended',
                                                      content_type='application/json',
                                                      content=json.dumps(req_dump),
                                                      method='POST',
                                                      authorization=access_token).create()

                    headers = {"Authorization": "Bearer %s" % access_token}
                    res = requests.post(self.payment_url, headers=headers, json=req_dump)

                    try:
                        res_json = res.json()
                    except ValueError:
                        res_json = res.content

                    PaymentProviderOperation(transaction_id=collection.id,
                                             payment_provider_id=self.payment_provider.id,
                                             operation_type='response',
                                             direction='received',
                                             content_type='application/json',
                                             content=json.dumps(res_json),
                                             status_code=res.status_code,
                                             parent_id=tm_req.id).create()

                    if res.status_code == requests.codes.ok:
                        result = (res_json['redirectUrl'], None)
                    else:
                        result = (None, res_json)
            else:
                result = (None, 'null_token')
        else:
            result = (None, 'request_error')
        return result

    def payment_callback(self, data):

        collection = CollectionTransaction.query.filter_by(display_id=data['merchantTransactionId'],
                                                           status='pending').one_or_none()
        if collection:
            request_origin = PaymentProviderOperation.query.filter_by(transaction_id=collection.id,
                                                                      operation_type='request',
                                                                      direction='sended').one_or_none()
            if request_origin:
                PaymentProviderOperation(transaction_id=collection.id,
                                         payment_provider_id=self.payment_provider.id,
                                         operation_type='request',
                                         direction='received',
                                         content_type='application/x-www-form-urlencoded',
                                         content=json.dumps(data),
                                         method='POST',
                                         parent_id=request_origin.id).create()
                if data['transactionStatus'] == 'success':
                    collection_data = json.loads(collection.data)
                    debt_schema = PartnerDebtSchema(many=True)
                    debts, error = debt_schema.load(collection_data['debts'])

                    if debts and not error:
                        if not PartnerCollectionWay.query.filter_by(id_transaccion=collection.id).one_or_none():
                            PartnerCollection.create_collection(debts, 'tigo_money', collection.id)
                            collection.status = data['transactionStatus']
                            db.session.commit()
