# -*- coding: utf-8 -*-

import json
from functools import total_ordering

import requests
from requests.auth import HTTPBasicAuth

from ..models.payment_provider import PaymentProvider, PaymentProviderOperation
from ..models.collection import CollectionTransaction
from ..models.factusys import PartnerDebtSchema, PartnerCollection, PartnerCollectionWay
from ...api import db
from ..utils.responses import InternalResponse, IRStatus
from ..models.bancard_vpos import Token, Operation, Request, ResponseSchema
from decimal import Decimal


class BancardVposManager:

    def __init__(self):
        self.payment_provider = PaymentProvider.query.filter_by(name='bancard_vpos').one()
        self.single_buy = self.payment_provider.get_endpoint_by_name('SINGLE_BUY')
        self.return_url = self.payment_provider.get_endpoint_by_name('REDIRECT_URL')
        self.single_buy_rollback = self.payment_provider.get_endpoint_by_name('SINGLE_BUY_ROLLBACK')
        self.single_buy_confirmation = self.payment_provider.get_endpoint_by_name('SINGLE_BUY_CONFIRMATION')
        self.get_single_buy_confirmation = self.payment_provider.get_endpoint_by_name('GET_SINGLE_BUY_CONFIRMATION')
        self.public_key = self.payment_provider.get_config_by_name('PUBLIC_KEY')
        self.private_key = self.payment_provider.get_config_by_name('PRIVATE_KEY')

    def _get_token(self):
        pass

    def _log_request(self, req, collection):
        return PaymentProviderOperation(transaction_id=collection.id,
                                        payment_provider_id=self.payment_provider.id,
                                        operation_type='request',
                                        direction='sended',
                                        content_type='application/json',
                                        content=json.dumps(req),
                                        method='POST').create()

    def _log_response(self, res, req, collection):

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
                                 parent_id=req.id).create()

    def _single_buy(self, collection):
        # total_amount = 0.00
        # total_amount = Decimal(collection.amount)

        token = Token(private_key=self.private_key,
                      shop_process_id=collection.display_id,
                      amount=("%.2f" % collection.amount),
                      currency='PYG')

        operation = Operation(
            token=token,
            shop_process_id=collection.display_id,
            amount=("%.2f" % collection.amount),
            currency='PYG',
            description='Pago de cuota social',
            return_url=self.return_url,
            cancel_url=self.return_url)

        base_request = Request(
            public_key=self.public_key,
            operation=operation
        )

        request = base_request.get_json()

        if request:
            log_req = self._log_request(request, collection)
            response = requests.post(self.single_buy, json=request)
            self._log_response(response, log_req, collection)
            try:
                res_json = res.json()
                response_schema = ResponseSchema()
                result = response_schema.load(res_json)
            except ValueError:
                res_json = res.content

            if response.status_code == requests.codes.ok:
                result = InternalResponse()
            else:
                result = InternalResponse(status=IRStatus.fail,
                                          message="No se pudo procesar su pago. Por favor vuelva a intentar, "
                                                  "si el inconveniente persiste comuniquese con el comercio.")
        else:
            result = InternalResponse(status=IRStatus.fail,
                                      message="No se pudo procesar su pago. Por favor vuelva a intentar, "
                                              "si el inconveniente persiste comuniquese con el comercio.")

        return result

    def _single_buy_confirmation(self):
        pass

    def _single_buy_get_confirmation(self):
        pass

    def _single_buy_rollback(self):
        pass

    def payment_request(self, collection):
        self._single_buy(collection)




