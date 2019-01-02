# -*- coding: utf-8 -*-

import json
import requests
from ..models.payment_provider import PaymentProvider, PaymentProviderOperation
from ..models.collection import CollectionTransaction
from ..models.factusys import PartnerDebtSchema, PartnerCollection, PartnerCollectionWay
from ...api import db, app
from ..models.bancard_vpos import Token, Operation, Request, \
    SingleBuyConfirmRequestSchema, GetSingleBuyConfirmResponseSchema, SingleBuyRollbackResponseSchema
from ..utils.responses import response_with
from ..utils import responses as resp


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

        return_uri = self.return_url + '?merchantTransactionId=' + str(collection.display_id)
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
                return response_with(resp.SUCCESS_200, value={"redirectUri": redirect_uri})
            else:
                return response_with(resp.CUSTOM_SERVER_ERROR_500, message="No se pudo procesar su pago. Por favor "
                                                                            "vuelva a intentar, si el inconveniente "
                                                                            "persiste comuniquese con el comercio.")
        else:
            return response_with(resp.CUSTOM_SERVER_ERROR_500, message="No se pudo procesar su pago. Por favor "
                                                                         "vuelva a intentar, si el inconveniente "
                                                                         "persiste comuniquese con el comercio.")

    def _single_buy_confirmation(self, data):
        single_buy_confirm_request_schema = SingleBuyConfirmRequestSchema()
        request, error = single_buy_confirm_request_schema.load(data)

        if not error:
            operation = request.operation
            collection = CollectionTransaction.query.filter_by(display_id=operation.shop_process_id,
                                                               status='pending').one_or_none()

            if collection:
                request_origin = PaymentProviderOperation.query\
                    .filter(PaymentProviderOperation.transaction_id == collection.id,
                            PaymentProviderOperation.operation_type == 'request',
                            PaymentProviderOperation.direction == 'sended')\
                    .order_by(PaymentProviderOperation.id).all()
                if request_origin:
                    request_origin = request_origin[0]
                    PaymentProviderOperation(transaction_id=collection.id,
                                             payment_provider_id=self.payment_provider.id,
                                             operation_type='request',
                                             direction='received',
                                             content_type='application/json',
                                             content=json.dumps(data),
                                             method='POST',
                                             parent_id=request_origin.id).create()

                    collection.status = 'success' if operation.response_code == '00' else 'cancel'
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
                                db.session.commit()
                                return response_with(resp.SUCCESS_200)
                            else:
                                return response_with(resp.SERVER_ERROR_500)
                        else:
                            return response_with(resp.SERVER_ERROR_500)
                    else:
                        db.session.commit()
                        return response_with(resp.SUCCESS_200)
                else:
                    return response_with(resp.CALLBACK_INVALID_PARENT_OPERATION_422)
            else:
                app.logger.error(json.dumps(resp.CALLBACK_INVALID_TRANSACTION_422['message']) + ' | ' + json.dumps(data))
                return response_with(resp.CALLBACK_INVALID_TRANSACTION_422)
        else:
            app.logger.error(json.dumps(error) + ' | ' + json.dumps(data))
            return response_with(resp.CALLBACK_BAD_REQUEST_400)

    def _single_buy_get_confirmation(self, collection):
        token = Token(private_key=self.private_key,
                      shop_process_id=collection.display_id,
                      operation="get_confirmation")

        operation = Operation(
            token=token,
            shop_process_id=collection.display_id)

        base_request = Request(
            public_key=self.public_key,
            operation=operation
        )

        request = base_request.get_json()

        log_req = self._log_request(request, collection)
        response = requests.post(self.get_single_buy_confirmation, json=request)
        self._log_response(response, log_req, collection)

        return response

    def _single_buy_rollback(self, collection):
        token = Token(private_key=self.private_key,
                      shop_process_id=collection.display_id,
                      operation="rollback",
                      amount="0.00")

        operation = Operation(
            token=token,
            shop_process_id=collection.display_id)

        base_request = Request(
            public_key=self.public_key,
            operation=operation
        )

        request = base_request.get_json()

        log_req = self._log_request(request, collection)
        response = requests.post(self.single_buy_rollback, json=request)
        self._log_response(response, log_req, collection)

        return response

    def payment_request(self, collection):
        return self._single_buy(collection)

    def payment_callback(self, data):
        return self._single_buy_confirmation(data)

    def check_pending_collection(self, collection):
        result = 'pending', None
        response = self._single_buy_get_confirmation(collection)
        try:
            response_json = response.json()
            get_single_buy_confirm_response_schema = GetSingleBuyConfirmResponseSchema()
            response_obj, error = get_single_buy_confirm_response_schema.load(response_json)
            if not error:
                if response_obj.status == 'success':
                    confirmation = response_obj.confirmation
                    if confirmation.response_code == '00':
                        result = 'success', confirmation.ticket_number
                    else:
                        result = 'cancel_now', None
                else:
                    result = 'cancel', None
            else:
                result = 'pending', None

        except ValueError:
            result = 'pending', None

        # if response.status_code == requests.codes.ok:
        #     get_single_buy_confirm_response_schema = GetSingleBuyConfirmResponseSchema()
        #     response_obj, error = get_single_buy_confirm_response_schema.load(response.json())
        #     if not error:
        #         if response_obj.status == 'success':
        #             confirmation = response_obj.confirmation
        #             if confirmation.response_code == '00':
        #                 result = 'success', confirmation.ticket_number
        #             else:
        #                 result = 'cancel_now', None
        #         else:
        #             result = 'cancel', None
        #     else:
        #         result = 'pending', None
        # else:
        #     try:
        #         res_json = response.json()
        #     except ValueError:
        #         res_json = None
        #
        #     if res_json and res_json.get('status') and res_json['status'] == 'error':
        #         result = 'cancel', None
        #     else:
        #         result = 'pending', None

        return result

    def payment_rollback(self, collection):
        result = 'fail'
        response = self._single_buy_rollback(collection)
        try:
            response_json = response.json()
            single_buy_rollback_response_schema = SingleBuyRollbackResponseSchema()
            response_obj, error = single_buy_rollback_response_schema.load(response_json)
            if not error:
                msg_keys = response_obj.messages and [msg.key for msg in response_obj.messages] or []
                if response_obj.status == 'success' and 'RollbackSuccessful' in msg_keys:
                    result = 'success'
                elif response_obj.status == 'error':
                    if 'AlreadyRollbackedError' in msg_keys or 'PaymentNotFoundError' in msg_keys:
                        result = 'success'
        except ValueError:
            result = 'fail'

        return result
