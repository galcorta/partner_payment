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
from ..models.bancard_vpos import Token, Operation, BaseRequest, BaseRequestSchema


class BancardVposManager:

    def __init__(self):
        self.request_schema = BancardVposRequestSchema()
        self.payment_provider = PaymentProvider.query.filter_by(name='bancard_vpos').one()
        self.token_uri = self.payment_provider.get_endpoint_by_name('SINGLE_BUY')
        self.payment_url = self.payment_provider.get_endpoint_by_name('SINGLE_BUY_ROLLBACK')
        self.redirect_uri = self.payment_provider.get_endpoint_by_name('GET_SINGLE_BUY_CONFIRMATION')
        self.callback_uri = self.payment_provider.get_endpoint_by_name('SINGLE_BUY_CONFIRMATION')
        self.public_key = self.payment_provider.get_config_by_name('PUBLIC_KEY')
        self.private_key = self.payment_provider.get_config_by_name('PRIVATE_KEY')

    def _get_token(self):
        pass

    def _single_buy(self, collection):
        total_amount = 0.00
        total_amount += collection.amount

        token = Token(private_key=self.private_key,
                      shop_process_id=collection.display_id,
                      amount=("%.2f" % collection.amount),
                      currency='PYG')

        operation = Operation(
            token=token,
            shop_process_id=collection.display_id,
            amount=total_amount,
            currency='PYG',
            description='Pago de cuota social',
            return_url=self.redirect_uri)

        base_request = BaseRequest(
            public_key=self.public_key,
            operation=operation
        )

        request = base_request.get_json()

        if request:
            print(request)

    def _single_buy_confirmation(self):
        pass

    def _single_buy_get_confirmation(self):
        pass

    def _single_buy_rollback(self):
        pass

    def payment_request(self, collection):
        self._single_buy(collection)




