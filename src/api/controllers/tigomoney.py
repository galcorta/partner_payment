# -*- coding: utf-8 -*-

import json
import requests
from requests.auth import HTTPBasicAuth

from ..models.tigomoney import TigoMoneyRequestSchema
from ..models.payment_provider import PaymentProvider, PaymentProviderOperation
from ..models.collection import CollectionTransaction
from ..models.factusys import PartnerDebtSchema, PartnerCollection, PartnerCollectionWay
from ...api import db
from ..utils.responses import InternalResponse, IRStatus


class TigoMoneyManager:

    def __init__(self):
        self.request_schema = TigoMoneyRequestSchema()
        self.payment_provider = PaymentProvider.query.filter_by(name='tigo_money').one()
        self.token_uri = self.payment_provider.get_endpoint_by_name('TM_TOKEN_URI')
        self.payment_url = self.payment_provider.get_endpoint_by_name('TM_PAYMENT_URI')
        self.redirect_uri = self.payment_provider.get_endpoint_by_name('TM_REDIRECT_URI')
        self.callback_uri = self.payment_provider.get_endpoint_by_name('TM_CALLBACK_URI')
        self.api_key = self.payment_provider.get_config_by_name('TM_API_KEY')
        self.secret = self.payment_provider.get_config_by_name('TM_SECRET')

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
                        result = InternalResponse(value={"redirectUri": res_json['redirectUrl']})
                    else:
                        result = InternalResponse(status=IRStatus.fail,
                                                  message="No se pudo procesar su pago. Por favor vuelva a intentar, "
                                                  "si el inconveniente persiste comuniquese con el comercio.")
            else:
                return InternalResponse(status=IRStatus.fail,
                                        message="Error al intentar obtener token de autorización de tigo")
        else:
            return InternalResponse(status=IRStatus.fail_400, message="Request inválido!")

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
                collection.status = data['transactionStatus']
                collection.payment_provider_voucher = data['mfsTransactionId']
                if data['transactionStatus'] == 'success':
                    collection_data = json.loads(collection.data)
                    debt_schema = PartnerDebtSchema(many=True, only=['id', 'amount'])
                    debts, error = debt_schema.load(collection_data['debts'])

                    if debts and not error:
                        if not PartnerCollectionWay.query.filter_by(collection_transaction_id=collection.id)\
                                .one_or_none():
                            PartnerCollection.create_collection(debts, self.payment_provider, collection)
                            db.session.commit()
                        else:
                            raise
                    else:
                        raise
                else:
                    db.session.commit()
            else:
                raise
        else:
            raise
