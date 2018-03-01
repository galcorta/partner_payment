# -*- coding: utf-8 -*-
import json
from datetime import date, timedelta
from flask import g
from ..utils.responses import InternalResponse, IRStatus
from ..models.payment_provider import PaymentProvider
from ..models.factusys import PartnerDebtSchema, PartnerDebt
from ..models.collection import CollectionTransaction
from .tigomoney import TigoMoneyManager
from .red_cobranza import RedCobranzaManager
from .bancard_vpos import BancardVposManager
from sqlalchemy import extract, not_


class CollectionController:

    def __init__(self, data):
        self.data = data

    def collect(self):
        debt_schema = PartnerDebtSchema(many=True, only=['id', 'amount'])
        debts, error = debt_schema.load(self.data['debts'])

        if not error:
            year_list = list(set([debt.fecha_vencimiento.year for debt in debts]))

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
                        return InternalResponse(status=IRStatus.fail_422,
                                                message="No puede pagar cuotas de forma desordenada dejando pendientes "
                                                        "deudas anteriores correspondientes al mismo periodo/año")

            band = False
            total_amount = 0
            for debt in debts:
                if debt.amount > 0:
                    total_amount += debt.amount
                else:
                    band = True

            if total_amount > 0 and not band:
                payment_provider = PaymentProvider.query \
                    .filter_by(name=self.data['payment_provider_data']['name'], active=True).one_or_none()

                partner_id = debts[0].id_cliente
                if payment_provider:
                    collection_transaction = CollectionTransaction(
                        context_id='partner_fee',
                        collection_entity_id=g.entity.id,
                        payment_provider_id=payment_provider.id,
                        amount=total_amount,
                        data=json.dumps(self.data),
                        partner_id=partner_id,
                        status='pending'
                    ).create()

                    payment_provider_type = payment_provider.get_config_by_name('TYPE')

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
                        return InternalResponse(status=IRStatus.fail_400,
                                                message="Nombre de proveedor de pago inválido!.")
                else:
                    return InternalResponse(status=IRStatus.fail_400,
                                            message="El proveedor de pago no existe en el sistema o no está habilitado.")
            else:
                return InternalResponse(status=IRStatus.fail_400,
                                        message="Monto de cuota a pagar igual o menor a cero.")
        else:
            return InternalResponse(status=IRStatus.fail_400,
                                    message="Datos de las cuotas a pagar mal informados.")

    def cancel(self, pp_name=None):
        if pp_name and pp_name == 'practipago':
            collection_transaction = CollectionTransaction.query\
                .filter(CollectionTransaction.payment_provider_voucher == self.data).one_or_none()
        else:
            collection_transaction = CollectionTransaction.query \
                .filter(CollectionTransaction.display_id == self.data).one_or_none()

        if collection_transaction:
            if collection_transaction.status == 'success':
                if collection_transaction.create_date.date() == date.today() or \
                        collection_transaction.create_date.date() == date.today()-timedelta(days=1):
                    red_cobranza_manager = RedCobranzaManager()
                    return red_cobranza_manager.payment_cancel(collection_transaction)
                else:
                    return InternalResponse(status=IRStatus.fail_422,
                                            message="La operación no se puede anular, ha sido creada hace mas de un dia.")
            else:
                return InternalResponse(status=IRStatus.fail_422, message="La operación que intenta anular ya ha sido "
                                                                          "anulada")
        else:
            return InternalResponse(status=IRStatus.fail_422, message="La operación que intenta anular no existe.")
