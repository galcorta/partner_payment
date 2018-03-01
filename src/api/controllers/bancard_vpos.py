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
from ..models.bancard_vpos import Token, Operation, Request, SingleBuyConfirmRequestSchema
from decimal import Decimal


class BancardVposManager:

    def __init__(self):
        self.payment_provider = PaymentProvider.query.filter_by(name='bancard_vpos').one()
        self.single_buy = self.payment_provider.get_endpoint_by_name('SINGLE_BUY')
        self.return_url = self.payment_provider.get_endpoint_by_name('RETURN_URL')
        self.single_buy_rollback = self.payment_provider.get_endpoint_by_name('SINGLE_BUY_ROLLBACK')
        self.single_buy_confirmation = self.payment_provider.get_endpoint_by_name('SINGLE_BUY_CONFIRMATION')
        self.get_single_buy_confirmation = self.payment_provider.get_endpoint_by_name('GET_SINGLE_BUY_CONFIRMATION')
        self.redirect_vpos_url = self.payment_provider.get_endpoint_by_name('REDIRECT_VPOS_URL')
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

        token = Token(private_key=self.private_key,
                      shop_process_id=collection.display_id,
                      amount=("%.2f" % collection.amount),
                      currency='PYG')

        return_uri = self.return_url + '?merchantTransactionId=' + collection.display_id
        operation = Operation(
            token=token,
            shop_process_id=collection.display_id,
            amount=("%.2f" % collection.amount),
            currency='PYG',
            description='Pago de cuota social',
            return_url=return_uri,
            cancel_url=return_uri)

        base_request = Request(
            public_key=self.public_key,
            operation=operation
        )

        request = base_request.get_json()

        if request:
            log_req = self._log_request(request, collection)
            response = requests.post(self.single_buy, json=request)
            self._log_response(response, log_req, collection)

            if response.status_code == requests.codes.ok:
                redirect_uri = self.redirect_vpos_url + '?process_id=' + response.json()['process_id'] \
                               + '&from_mobile=false'
                result = InternalResponse(value={"redirectUri": redirect_uri})
            else:
                result = InternalResponse(status=IRStatus.fail,
                                          message="No se pudo procesar su pago. Por favor vuelva a intentar, "
                                                  "si el inconveniente persiste comuniquese con el comercio.")
        else:
            result = InternalResponse(status=IRStatus.fail,
                                      message="No se pudo procesar su pago. Por favor vuelva a intentar, "
                                              "si el inconveniente persiste comuniquese con el comercio.")

        return result

    def _single_buy_confirmation(self, data):
        result = InternalResponse()
        single_buy_confirm_request_schema = SingleBuyConfirmRequestSchema()
        request, error = single_buy_confirm_request_schema.load(data)

        if not error:
            operation = request.operation
            collection = CollectionTransaction.query.filter_by(display_id=operation.shop_process_id,
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
                                             content_type='application/json',
                                             content=json.dumps(data),
                                             method='POST',
                                             parent_id=request_origin.id).create()

                    collection.status = 'success' if operation.response_code == '00' else 'canceled'
                    collection.payment_provider_voucher = operation.ticket_number

                    if collection.status == 'success':
                        collection_data = json.loads(collection.data)
                        debt_schema = PartnerDebtSchema(many=True, only=['id', 'amount'])
                        debts, error = debt_schema.load(collection_data['debts'])

                        if debts and not error:
                            if not PartnerCollectionWay.query.filter_by(collection_transaction_id=collection.id)\
                                    .one_or_none():
                                partner_collection = PartnerCollection()
                                partner_collection.create(debts, collection)
                                # PartnerCollection.create_collection(debts, self.payment_provider, self.collection)
                                db.session.commit()
                            else:
                                result = InternalResponse(status=IRStatus.fail)
                        else:
                            result = InternalResponse(status=IRStatus.fail)
                    else:
                        db.session.commit()
                        result = InternalResponse(status=IRStatus.fail)
                else:
                    result = InternalResponse(status=IRStatus.fail)
            else:
                result = InternalResponse(status=IRStatus.fail)
        else:
            result = InternalResponse(status=IRStatus.fail)

        return result

    def _single_buy_get_confirmation(self):
        pass

    def _single_buy_rollback(self):
        pass

    def payment_request(self, collection):
        return self._single_buy(collection)

    def payment_callback(self, data):
        return self._single_buy_confirmation(data)
