# -*- coding: utf-8 -*-
import json
from datetime import date, datetime, timedelta
from flask import g
# from ..utils.responses import InternalResponse, IRStatus
from ..utils.responses import response_with
from ..utils import responses as resp
from ..models.payment_provider import PaymentProvider, PaymentProviderOperation
from ..models.factusys import PartnerDebtSchema, PartnerDebt, PartnerCollectionWay, PartnerCollection
from ..models.collection import CollectionTransaction, WebPortalNotification
from .tigomoney import TigoMoneyManager
from .red_cobranza import RedCobranzaManager
from .bancard_vpos import BancardVposManager
from sqlalchemy import extract, not_
from ...api import db


class CollectionController:

    def __init__(self, data):
        self.data = data

    def collect(self):
        debt_schema = PartnerDebtSchema(many=True, only=['id', 'amount'])
        debts, error = debt_schema.load(self.data['debts'])

        if not error and debts:
            year_list = list(set([debt.fecha_vencimiento.year for debt in debts]))

            # Valida que no se paguen las cuotas desordenadamente
            for year in year_list:
                debt_list = [debt for debt in debts if debt.fecha_vencimiento.year == year]
                debt_id_list = [debt.id for debt in debts if debt.fecha_vencimiento.year == year]
                for dbt in debt_list:
                    query = PartnerDebt.query.filter(PartnerDebt.id_cliente == dbt.id_cliente,
                                                     extract('year', PartnerDebt.fecha_vencimiento) == year,
                                                     PartnerDebt.id < dbt.id,
                                                     PartnerDebt.estado == "Pendiente",
                                                     not_(PartnerDebt.id.in_(debt_id_list)))\
                        .order_by(PartnerDebt.fecha_vencimiento)
                    fetched = query.all()
                    if fetched:
                        return response_with(resp.DISORDERED_FEE_PAYMENT_422)

            # Valida que el monto a pagar sea mayor a cero, que la cuota no este cancelada o
            # que se intente abonar un monto mayor al monto de la cuota
            band = False
            total_amount = 0
            for debt in debts:
                if debt.amount > 0:
                    total_amount += debt.amount
                else:
                    return response_with(resp.FEE_BAD_REQUEST_400)

                if debt.estado == 'Cobrado' or debt.saldo == 0:
                    return response_with(resp.FEE_CANCELED_REQUEST_422)

                if debt.amount > debt.saldo:
                    return response_with(resp.FEE_AMOUNT_EXCEEDED_422)

            if total_amount > 0 and not band:
                payment_provider = PaymentProvider.query \
                    .filter_by(name=self.data['payment_provider_data']['name'], active=True).one_or_none()

                if payment_provider:
                    payment_provider_type = payment_provider.get_config_by_name('TYPE')
                    if payment_provider_type == 'RED_COBRANZA':
                        # Valida que la red de cobranza no envie un voucher repetido
                        coll_trx = CollectionTransaction.query.filter(
                            CollectionTransaction.payment_provider_id == payment_provider.id,
                            CollectionTransaction.payment_provider_voucher ==
                            self.data['payment_provider_data']['voucher']).one_or_none()
                        if coll_trx:
                            return response_with(resp.VOUCHER_EXISTENT_422)

                    partner_id = debts[0].id_cliente
                    collection_transaction = CollectionTransaction(
                        context_id='partner_fee',
                        collection_entity_id=g.entity.id,
                        payment_provider_id=payment_provider.id,
                        amount=total_amount,
                        data=json.dumps(self.data),
                        partner_id=partner_id,
                        status='pending'
                    ).create()

                    if payment_provider.name == 'tigo_money':
                        tm_manager = TigoMoneyManager()
                        return tm_manager.payment_request(collection_transaction)

                    elif payment_provider.name == 'bancard_vpos':
                        vpos_manager = BancardVposManager()
                        return vpos_manager.payment_request(collection_transaction)

                    elif payment_provider_type == 'RED_COBRANZA':
                        red_cobranza_manager = RedCobranzaManager()
                        return red_cobranza_manager.payment_request(debts, collection_transaction)
                    else:
                        return response_with(resp.INVALID_PAYMENT_PROVIDER_NAME_400)
                else:
                    return response_with(resp.INVALID_PAYMENT_PROVIDER_400)
            else:
                return response_with(resp.FEE_AMOUNT_INVALID_400)
        else:
            return response_with(resp.FEE_BAD_REQUEST_400)

    def cancel(self):
        collection_transaction = CollectionTransaction.query\
            .filter(CollectionTransaction.payment_provider_voucher == self.data,
                    CollectionTransaction.collection_entity_id == g.entity.id).one_or_none()

        if collection_transaction:
            if collection_transaction.status == 'success':
                if collection_transaction.create_date.date() == date.today() or \
                        collection_transaction.create_date.date() == date.today()-timedelta(days=1):
                    red_cobranza_manager = RedCobranzaManager()
                    return red_cobranza_manager.payment_cancel(collection_transaction)
                else:
                    return response_with(resp.EXPIRED_TIME_TO_CANCEL_TRANSACTION_422)
            else:
                return response_with(resp.ALREADY_CANCELED_TRANSACTION_422)
        else:
            return response_with(resp.INVALID_TRANSACTION_422)

    def clear_pending_collection(self):
        pending_collections = CollectionTransaction.query.filter(CollectionTransaction.partner_id == self.data,
                                                                 CollectionTransaction.status == 'pending').all()
        pending_debt_ids = []
        for coll in pending_collections:
            result = 'pending'
            data = json.loads(coll.data)
            payment_provider = PaymentProvider.query.filter_by(name=data['payment_provider_data']['name'],
                                                               active=True).one_or_none()
            if payment_provider:
                if payment_provider.name == 'bancard_vpos':
                    bancard_vpos_manager = BancardVposManager()
                    status, pp_voucher = bancard_vpos_manager.check_pending_collection(coll)
                elif payment_provider.name == 'tigo_money':
                    tigo_money_manager = TigoMoneyManager()
                    status, pp_voucher = tigo_money_manager.payment_get_confirmation(coll)
                else:
                    status, pp_voucher = 'pending', None

                if status == 'success':
                    debt_schema = PartnerDebtSchema(many=True, only=['id', 'amount'])
                    debts, error = debt_schema.load(data['debts'])
                    if debts and not error:
                        coll.status = status
                        coll.payment_provider_voucher = pp_voucher
                        if not PartnerCollectionWay.query.filter_by(collection_transaction_id=coll.id) \
                                .one_or_none():
                            partner_collection = PartnerCollection()
                            partner_collection.create(debts, coll)
                        result = 'success'
                        db.session.commit()

                elif status == 'cancel' or status == 'cancel_now':
                    if payment_provider.name == 'bancard_vpos':
                        if status == 'cancel_now' or (coll.create_date + timedelta(minutes=11)) < datetime.now():
                            vpos_manager = BancardVposManager()
                            res = vpos_manager.payment_rollback(coll)
                            if res == 'success':
                                coll.status = 'cancel'
                                coll.payment_provider_voucher = coll.payment_provider_voucher or pp_voucher
                                db.session.commit()
                                result = 'cancel'
                            else:
                                result = 'pending'
                        else:
                            result = 'pending'
                    elif payment_provider.name == 'tigo_money':
                        coll.status = status
                        coll.payment_provider_voucher = coll.payment_provider_voucher or pp_voucher
                        db.session.commit()
                        result = 'cancel'
                else:
                    result = 'pending'

            if result == 'pending':
                content = 'Usted ha iniciado un pago en linea (TigoMoney o Bancard). Pueden trascurrir diez minutos desde que ' \
                          'realizo el pago hasta que recibamos la respuesta "confirmando" o "cancelando" la ' \
                          'operación. Hasta entonces no puede abonar otras cuotas. Por favor aguarde unos minutos ' \
                          'mas y vuelva a ingresar al portal. Si la situación persiste comuniquese con la ' \
                          'administración del Club. Gracias.'

                WebPortalNotification(
                    content=content.decode('utf-8'),
                    notification_type='info',
                    partner_id=coll.partner_id
                ).create()

                pending_debt_ids.extend([d['id'] for d in data['debts']])

        return pending_debt_ids

    def get_collection_description(self):
        pp_operations = PaymentProviderOperation.query.filter(PaymentProviderOperation.transaction_id == self.data.id,
                                                              PaymentProviderOperation.direction == 'received',
                                                              PaymentProviderOperation.operation_type == 'request')\
            .order_by(PaymentProviderOperation.create_date).all()

        result = ''
        if pp_operations:
            pp_operations = pp_operations[-1]
            content = json.loads(pp_operations.content)
            if content.get('operation'):
                operation = content['operation']
                if operation.get('response_description'):
                    result = operation['response_description']
        return result
