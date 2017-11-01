#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from flask import Blueprint
from flask import request
from ..utils.responses import response_with
from ..utils import responses as resp
from ..models.model_author import Author, AuthorSchema
from ..models.model_partner import Partner, PartnerLoginSchema, PartnerSchema, PartnerLoginResponseSchema
from ..models.model_debt import Debt, DebtSchema
from ..models.model_collection import Collection, CollectionDetail, CollectionWay, CreateCollectionSchema
# from ..models.model_payment_providers import TigoMoneyPaymentReq
from ...api import db
import json
from ..utils.crypt import bcrypt

route_path_general = Blueprint("route_path_general", __name__)


@route_path_general.route('/v1.0/authenticate', methods=['POST'])
def authenticate():
    """
        Partner login
        ---
        parameters:
            - in: body
              name: body
              description: Login of the partner
              schema:
                id: Partner
                required:
                    - username
                    - password
                properties:
                    username:
                        type: string
                        description: Username of the partner
                    password:
                        type: string
                        description: Password of the partner

        responses:
                200:
                    description: Partner successfully login
                    schema:
                      id: PartnerSuccessLogin
                      properties:
                        code:
                          type: string
                        user:
                            id: PartnerLogin
                            properties:
                                name:
                                    type: string
                                token:
                                    type: string
                403:
                    description: Invalid credentials
                    schema:
                        id: invalidCredentials
                        properties:
                            code:
                                type: string
                            message:
                                type: string
        """
    try:
        data = request.get_json()
        partner_schema_login = PartnerLoginSchema()
        partner_login, error = partner_schema_login.load(data)
        partner = Partner.query.filter_by(documento_identidad=partner_login['username']).first()
        if partner and partner.nombre:
            first3_name = partner.nombre.lower().strip()[:3]
            last3_ci = partner.documento_identidad.strip()[-3:]
            correct_password = first3_name + last3_ci
            if partner_login['password'].lower() == correct_password:
                partner.token = 'este-es-el-token'
                partner.name = partner.nombre
                login_response_schema = PartnerLoginResponseSchema()
                result = login_response_schema.dump(partner).data
                return response_with(resp.SUCCESS_200, value={"user": result})
            else:
                return response_with(resp.UNAUTHORIZED_403)
        else:
            return response_with(resp.UNAUTHORIZED_403)
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/v1.0/partner/<int:partner_id>/debt', methods=['GET'])
def get_partner_debt(partner_id):
    """
        List partner debts
        ---
        responses:
                200:
                    description: Returns debt list
                    schema:
                      id: DebtList
                      properties:
                        code:
                          type: string
                        message:
                          type: string
                        debts:
                            type: array
                            items:
                                schema:
                                    id: DebtSummary
                                    properties:
                                        id_cuota:
                                            type: integer
                                        mes:
                                            type: string
                                        monto:
                                            type: integer
                                        saldo_x_pagar:
                                            type: integer
                                        vencimiento:
                                            type: string
                                        anno:
                                            type: string
        """
    # partner = Partner.query.filter_by(id_socio=partner_id).first()

    query = Debt.query.filter(Debt.id_socio == partner_id).filter(Debt.saldo_x_cobrar > 0).order_by(Debt.anio)
    fetched = query.all()

    # debts_dict = dict()
    # for debt in fetched:
    #     if debt.anno not in debts_dict:
    #         debts_dict[debt.anno] = []
    #     debts_dict[debt.anno].append({'id_cuota': debt.id_cuota,
    #                             'mes': debt.mes,
    #                             'monto': debt.monto,
    #                             'saldo_x_pagar': debt.saldo_x_pagar,
    #                             'vencimiento': debt.vencimiento})
    # debt_list = []
    # for period in list(debts_dict):
    #     debt_list.append({'period': period, 'debts': debts_dict[period]})

    debt_schema = DebtSchema(many=True, only=['id_cuota', 'mes', 'monto_cobrado', 'saldo_x_cobrar', 'vencimiento', 'anio'])
    debts, error = debt_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"debts": debts})


@route_path_general.route('/v1.0/collection', methods=['POST'])
def create_collection():
    """
        Collection of fees
        ---
        parameters:
            - in: body
              name: body
              schema:
                id: DebtCollect
                required:
                  - payment_method
                  - debts
                properties:
                    payment_method:
                        type: string
                        description: Metodo de pago
                    debts:
                        type: array
                        description: Listado de cuotas cobradas
                        items:
                            schema:
                                id: DebtSchema
                                properties:
                                    id_cuota:
                                        type: integer
                                    amount:
                                        type: integer
                    payment_provider_data:
                        type: object

        responses:
                200:
                    description: Collection successfully created
                    schema:
                      id: CollectionCreated
                      properties:
                        code:
                          type: string
                        message:
                          type: string
                        comprobante:
                          type: string
                422:
                    description: Invalid input arguments
                    schema:
                        id: invalidInput
                        properties:
                            code:
                                type: string
                            message:
                                type: string
        """
    try:
        data = request.get_json()
        debt_schema = DebtSchema(many=True)
        debts, error = debt_schema.load(data['debts'])
        id_socio = debts[0].id_socio
        payment_method = data['payment_method']

        partner = Partner.query.get(id_socio)
        created_date = datetime.now()

        total_amount = 0
        collection_detail_list = []
        for debt in debts:
            total_amount += debt.amount
            collection_detail_list.append(CollectionDetail(id_cuota=debt.id_cuota,
                                                           monto=debt.amount,
                                                           fecha=created_date))
            debt.saldo_x_cobrar -= debt.amount

        collection_way_list = [CollectionWay(id_socio, partner.nro_socio, created_date, payment_method, total_amount)]

        collection = Collection(
            id_socio=partner.id_socio,
            fecha=created_date,
            nro_socio=partner.nro_socio,
            categoria=None,
            anno=None,
            monto_cobrado=total_amount,
            nro_recibo=None,
            estado=None,
            nota=None,
            details=collection_detail_list,
            collection_ways=collection_way_list
        )

        db.session.add(collection)
        db.session.commit()

        return response_with(resp.SUCCESS_200, value={"comprobante": collection.id_cobro})
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/v1.0/collection/tigo_money_payment', methods=['POST'])
def tigo_money_payment():
    """
            Tigo money payment
            ---
            parameters:
                - in: body
                  name: body
                  description: Tigo money payment
                  schema:
                    id: TigoMoneyPaymentRequest
                    required:
                        - master_merchant
                        - subscriber
                        - payment
                    properties:
                        master_merchant:
                            schema:
                                id: MasterMerchant
                                required:
                                    - account
                                    - pin
                                    - id
                                properties:
                                    account:
                                        type: string
                                    pin:
                                        type: string
                                    id:
                                        type: string
                        subscriber:
                            schema:
                                id: Subscriber
                                required:
                                    - account
                                    - country_code
                                    - country
                                    - email_id
                                properties:
                                    account:
                                        type: string
                                    country_code:
                                        type: string
                                    country:
                                        type: string
                                    email_id:
                                        type: string
                        payment:
                            schema:
                                id: Payment
                                required:
                                    - amount
                                    - currency_code
                                    - tax
                                    - fee
                                properties:
                                    amount:
                                        type: string
                                    currency_code:
                                        type: string
                                    tax:
                                        type: string
                                    fee:
                                        type: string

            responses:
                    200:
                        description: Tigo money payment success receive
                        schema:
                          id: TigoMoneyPaymentReturnSuccess
                          properties:
                            code:
                              type: string
                            message:
                              type: string
                    422:
                        description: Invalid input arguments
                        schema:
                            id: invalidInput
                            properties:
                                code:
                                    type: string
                                message:
                                    type: string
            """
    try:
        data = request.get_json()



        tigo_money_payment = TigoMoneyPaymentReq(json.dumps(data), 'pending')

        db.session.add(tigo_money_payment)
        db.session.commit()

        return response_with(resp.SUCCESS_200, value={"comprobante": tigo_money_payment.id})
    except Exception:
        return response_with(resp.INVALID_INPUT_422)
