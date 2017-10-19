#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from flask import Blueprint
from flask import request
from ..utils.responses import response_with
from ..utils import responses as resp
from ..models.model_author import Author, AuthorSchema
from ..models.model_partner import Partner, PartnerLoginSchema, PartnerSchema
from ..models.model_debt import Debt, DebtSchema
from ..models.model_collection import Collection

from ...api import db
from ..utils.crypt import bcrypt

route_path_general = Blueprint("route_path_general", __name__)


@route_path_general.route('/v1.0/login', methods=['POST'])
def login():
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
                    - documento_identidad
                    - password
                properties:
                    documento_identidad:
                        type: string
                        description: Identity document of the partner
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
                        message:
                          type: string
                        partner:
                            id: PartnerLogin
                            properties:
                                nombre:
                                    type: string
                                nro_socio:
                                    type: integer
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
        partner = Partner.query.filter_by(documento_identidad=partner_login['documento_identidad']).first()
        if partner and partner.nombre:
            first3_name = partner.nombre.lower().strip()[:3]
            last3_ci = partner.documento_identidad.strip()[-3:]
            correct_password = first3_name + last3_ci
            if partner_login['password'].lower() == correct_password:
                partner_schema = PartnerSchema()
                result = partner_schema.dump(partner).data
                return response_with(resp.SUCCESS_200, value={"partner": result})
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

    query = Debt.query.filter(Debt.id_socio == partner_id).filter(Debt.saldo_x_pagar > 0).order_by(Debt.anno)
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

    debt_schema = DebtSchema(many=True, only=['id_cuota', 'mes', 'monto', 'saldo_x_pagar', 'vencimiento', 'anno'])
    debts, error = debt_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={"debts": debts})


@route_path_general.route('/v1.0/payment', methods=['POST'])
def create_collection():
    """
        Payment of fees
        ---
        parameters:
            - in: body
              name: body
              schema:
                id: DebtCollect
                type: array
                description: Listado de cuotas cobradas
                items:
                    schema:
                        id: DebtSchema
                        properties:
                            id_cuota:
                                type: integer
                            saldo_x_pagar:
                                type: integer
        responses:
                200:
                    description: Author successfully created
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
        debts, error = debt_schema.load(data)
        # debts = debts_dict['debts']
        # for item in debts:
        #     debt = Debt.query.get(item.id_cuota)
        #     debt.saldo_x_pagar = item.saldo_x_pagar

        id_socio = debts[0].id_socio
        partner = Partner.query.get(id_socio)

        collect = Collection(
            id_socio=partner.id_socio,
            efectivo=sum((item.monto - item.saldo_x_pagar) for item in debts),
            fecha=datetime.now(),
            forma_de_pago='on_line',
            nro_socio=partner.nro_socio,
            cantidad_de_cuotas=len(debts),
            cuotas_afectadas=', '.join(str(item.id_cuota) for item in debts),
            comprobante='dev',
        )

        db.session.add(collect)
        db.session.commit()

        return response_with(resp.SUCCESS_200, value={"comprobante": collect.comprobante})
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


# @route_path_general.route('/v1.0/authors', methods=['POST'])
# def create_author():
#     """
#     Create author endpoint
#     ---
#     parameters:
#         - in: body
#           name: body
#           schema:
#             id: Author
#             required:
#                 - name
#                 - surname
#                 - books
#             properties:
#                 name:
#                     type: string
#                     description: First name of the author
#                     default: "John"
#                 surname:
#                     type: string
#                     description: Surname of the author
#                     default: "Doe"
#                 books:
#                     type: string
#                     description: Book list of author
#                     type: array
#                     items:
#                         schema:
#                             id: BookSchema
#                             properties:
#                                 title:
#                                     type: string
#                                     default: "My First Book"
#                                 year:
#                                     type: date
#                                     default: "1989-01-01"
#     responses:
#             200:
#                 description: Author successfully created
#                 schema:
#                   id: AuthorCreated
#                   properties:
#                     code:
#                       type: string
#                     message:
#                       type: string
#                     value:
#                       schema:
#                         id: AuthorFull
#                         properties:
#                             name:
#                                 type: string
#                             surname:
#                                 type: string
#                             books:
#                                 type: array
#                                 items:
#                                     schema:
#                                         id: BookSchema
#             422:
#                 description: Invalid input arguments
#                 schema:
#                     id: invalidInput
#                     properties:
#                         code:
#                             type: string
#                         message:
#                             type: string
#     """
#     try:
#         data = request.get_json()
#         author_schema = AuthorSchema()
#         author, error = author_schema.load(data)
#         result = author_schema.dump(author.create()).data
#         return response_with(resp.SUCCESS_200, value={"author": result})
#     except Exception:
#         return response_with(resp.INVALID_INPUT_422)
#
#
# @route_path_general.route('/v1.0/authors', methods=['GET'])
# def get_author_list():
#     """
#     Get author list
#     ---
#     responses:
#             200:
#                 description: Returns author list
#                 schema:
#                   id: AuthorList
#                   properties:
#                     code:
#                       type: string
#                     message:
#                       type: string
#                     authors:
#                         type: array
#                         items:
#                             schema:
#                                 id: AuthorSummary
#                                 properties:
#                                     name:
#                                         type: string
#                                     surname:
#                                         type: string
#     """
#     fetched = Author.query.all()
#     author_schema = AuthorSchema(many=True, only=['name', 'surname'])
#     authors, error = author_schema.dump(fetched)
#     return response_with(resp.SUCCESS_200, value={"authors": authors})
#
#
# @route_path_general.route('/v1.0/authors/<int:author_id>', methods=['GET'])
# def get_author_detail(author_id):
#     """
#     Get author detail
#     ---
#     parameters:
#         - name: author_id
#           in: path
#           description: ID of the author
#           required: true
#           schema:
#             type: integer
#
#     responses:
#             200:
#                 description: Returns author detail
#                 schema:
#                   id: AuthorList
#                   properties:
#                     code:
#                       type: string
#                     message:
#                       type: string
#                     author:
#                         id: AuthorFull
#                         properties:
#                             name:
#                                 type: string
#                             surname:
#                                 type: string
#                             books:
#                                 type: array
#                                 items:
#                                     schema:
#                                         id: BookSchema
#                                         properties:
#                                             title:
#                                                 type: string
#                                             year:
#                                                 type: date
#     """
#     fetched = Author.query.filter_by(id=author_id).first()
#     author_schema = AuthorSchema()
#     author, error = author_schema.dump(fetched)
#     return response_with(resp.SUCCESS_200, value={"author": author})

@route_path_general.route('/v1.0/payment_providers/bancard', methods=['POST'])
def bancard_return():
    """
            Bancard return
            ---
            parameters:
                - in: body
                  name: body
                  description: Confirmation from bancard (success/error)
                  schema:
                    id: BancardReturn
                    required:
                        - transaction
                        - status
                        - voucher
                    properties:
                        transaction:
                            type: string
                            description: bancard transaction ID
                        status:
                            type: string
                            description: transaction status
                        voucher:
                            type: string
                            description: transaction voucher
            responses:
                    200:
                        description: Bancard return success receive
                        schema:
                          id: BancardReturnSuccess
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
    pass


@route_path_general.route('/v1.0/payment_providers/botontigo', methods=['POST'])
def boton_tigo_return():
    """
            Boton Tigo return
            ---
            parameters:
                - in: body
                  name: body
                  description: Confirmation from Boton Tigo (success/error)
                  schema:
                    id: BotonTigo
                    required:
                        - transaction
                        - status
                        - voucher
                    properties:
                        transaction:
                            type: string
                            description: tigo transaction ID
                        status:
                            type: string
                            description: transaction status
                        voucher:
                            type: string
                            description: transaction voucher
            responses:
                    200:
                        description: Boton Tigo return success receive
                        schema:
                          id: BotonTigoReturnSuccess
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
    pass