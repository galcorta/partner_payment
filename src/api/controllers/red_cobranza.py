# -*- coding: utf-8 -*-
import json
from ..utils.responses import response_with
from ..utils import responses as resp
from ..models.factusys import PartnerCollection
from ...api import db
from ..models.red_cobranza import RedCobranzaRequestSchema


class RedCobranzaManager:

    def __init__(self):
        self.request_schema = RedCobranzaRequestSchema()

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
            partner_collection = PartnerCollection()
            partner_collection.create(debts, collection)
            collection.status = 'success'
            db.session.commit()
            return response_with(resp.SUCCESS_200, value={"transaction_id": collection.display_id})
        else:
            return response_with(resp.INVALID_PAYMENT_PROVIDER_DATA_400)

    def payment_cancel(self, collection):
        try:
            partner_collection = PartnerCollection.get_by_collection(collection)
            partner_collection.cancel_collection()
            collection.status = 'cancel'
            db.session.commit()
            return response_with(resp.SUCCESS_200, message="Operación anulada exitosamente!.")
        except Exception, e:
            return response_with(resp.SERVER_ERROR_500)
