# -*- coding: utf-8 -*-
import json
from ..utils.responses import InternalResponse, IRStatus
from ..models.payment_provider import PaymentProvider
from ..models.factusys import PartnerCollection
from ...api import db
from ..models.red_cobranza import RedCobranzaRequestSchema


class RedCobranzaManager:

    def __init__(self):
        self.request_schema = RedCobranzaRequestSchema()
        self.payment_provider = PaymentProvider.query.filter_by(name='red_cobranza').one()

    def _request_treatment(self, collection):
        request, error = self.request_schema.load(json.loads(collection.data)['payment_provider_data'])
        if not error:
            return self.request_schema.dump(request)
        else:
            return None, True

    def payment_request(self, debts, collection):
        req_dump, error = self._request_treatment(collection)
        if not error:
            collection.payment_provider_voucher = req_dump['voucher']
            PartnerCollection.create_collection(debts, self.payment_provider, collection)
            collection.status = 'success'
            db.session.commit()
            return InternalResponse(value={"transaction_id": collection.display_id})
        else:
            return InternalResponse(status=IRStatus.fail_400, message="Request inválido!")
