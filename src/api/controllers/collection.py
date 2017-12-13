# -*- coding: utf-8 -*-
import json
from flask import g
from ..utils.responses import InternalResponse, IRStatus
from ..models.payment_provider import PaymentProvider
from ..models.factusys import PartnerCollection, PartnerDebtSchema
from ..models.collection import CollectionTransaction
from .tigomoney import TigoMoneyManager
from .red_cobranza import RedCobranzaManager
from ...api import db


class CollectionController:

    def __init__(self, data):
        self.data = data

    def collect(self):
        debt_schema = PartnerDebtSchema(many=True, only=['id', 'amount'])
        debts, error = debt_schema.load(self.data['debts'])
        if not error:
            # total_amount = sum([debt.amount for debt in debts])
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

                if payment_provider:
                    collection_transaction = CollectionTransaction(
                        context_id='partner_fee',
                        collection_entity_id=g.entity.id,
                        payment_provider_id=payment_provider.id,
                        amount=total_amount,
                        data=json.dumps(self.data),
                        status='pending'
                    ).create()

                    if payment_provider.name == 'tigo_money':
                        tm_manager = TigoMoneyManager()
                        return tm_manager.payment_request(collection_transaction)

                    elif payment_provider.name == 'bancard_vpos':
                        pass

                    elif payment_provider.name == 'red_cobranza':
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