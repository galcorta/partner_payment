# -*- coding: utf-8 -*-

import json
from flask import Blueprint
from flask import request
from flask import g
from ..utils.responses import response_with
from ..utils import responses as resp
from ..models.partner import Partner, PartnerLoginSchema, PartnerLoginResponseSchema, PartnerCollection
from ..models.partner_debt import PartnerDebt, PartnerDebtSchema
from ..models.collection import CollectionTransaction
from ..models.tigomoney import TigoMoneyManager
from ..models.user import User, UserSchema
from ..utils.auth import auth, auth_tk


route_path_general = Blueprint("route_path_general", __name__)


@route_path_general.route('/1.0/token', methods=['POST'])
@auth.login_required
def get_auth_token():
    try:
        token = g.user.generate_auth_token(300)
        return response_with(resp.ACCESS_TOKEN_200, value={'access_token': token.decode('ascii')})
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


#  Solo se utiliza desde la web
@route_path_general.route('/1.0/partners/authenticate', methods=['POST'])
@auth.login_required
def partner_authenticate():
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
            if partner.verify_password(partner_login['password']):
                access_token = g.user.generate_auth_token(300)
                partner.name = partner.nombre
                partner.username = partner.documento_identidad
                login_response_schema = PartnerLoginResponseSchema()
                result = login_response_schema.dump(partner).data
                return response_with(resp.SUCCESS_200, value={'user': result, 'access_token': access_token})
            else:
                return response_with(resp.UNAUTHORIZED_403)
        else:
            return response_with(resp.UNAUTHORIZED_403)
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/partners/<string:username>/debts', methods=['GET'])
@auth_tk.login_required
def get_partner_debt(username):
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
                                        id:
                                            type: integer
                                        mes:
                                            type: string
                                        saldo_x_cobrar:
                                            type: integer
                                        vencimiento:
                                            type: string
                                        anio:
                                            type: string
        """
    try:
        partner = Partner.query.filter_by(documento_identidad=username).one_or_none()
        if partner:
            query = PartnerDebt.query.filter(PartnerDebt.id_socio == partner.id).filter(PartnerDebt.saldo_x_cobrar > 0)\
                .order_by(PartnerDebt.anio)
            fetched = query.all()
            debt_schema = PartnerDebtSchema(many=True, only=['id', 'mes', 'saldo_x_cobrar', 'vencimiento', 'anio'])
            debts, error = debt_schema.dump(fetched)
            return response_with(resp.SUCCESS_200, value={"debts": debts})
        else:
            return response_with(resp.INVALID_INPUT_422,
                                 message='El número de cédula proveído no existe en el sistema.')
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/partners/collection', methods=['POST'])
@auth_tk.login_required
def create_partner_collection():
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
                                id: PartnerDebtSchema
                                properties:
                                    id:
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
    # try:
    data = request.get_json()
    debt_schema = PartnerDebtSchema(many=True)
    debts, error = debt_schema.load(data['debts'])
    total_amount = sum([debt.amount for debt in debts])
    payment_provider = data['payment_method']
    collection_transaction = CollectionTransaction(
        context_id='partner_fee',
        provider=payment_provider,
        amount=total_amount,
        data=json.dumps(data),
        status='pending'
    ).create()

    if payment_provider == 'tigo_money':
        tm_manager = TigoMoneyManager()
        redirect_uri, error = tm_manager.payment_request(collection_transaction)
        if redirect_uri:
            return response_with(resp.REDIRECT_200, value={"redirect_uri": redirect_uri})
        else:
            if error == 'null_token':
                return response_with(resp.SERVER_ERROR_500,
                                     message='Error al intentar obtener token de autorización de tigo')
            else:
                return response_with(resp.BAD_REQUEST_400)

    elif payment_provider == 'bancard_vpos':
        pass

    else:
        collection = PartnerCollection.create_collection(debts, payment_provider, collection_transaction.id)
        return response_with(resp.SUCCESS_200, value={"comprobante": collection.id_cobro})
    # except Exception:
    #     return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/payment_providers/tigo/callback', methods=['POST'])
def tigo_callback():
    """
            Tigo Callback
            ---
            parameters:
                - in: formData
                  name: transactionStatus
                  required: true
                  type: string
                  description: Transaction status success/fail
                - in: formData
                  name: merchantTransactionId
                  required: false
                  type: string
                  description: Identificador proveido por el merchant
                - in: formData
                  name: mfsTransactionId
                  required: false
                  type: string
                  description: ID de transacción generado en la plataforma de Tigo Money
                - in: formData
                  name: accessToken
                  required: false
                  type: string
                  description: Token utilizado
                - in: formData
                  name: transactionCode
                  required: false
                  type: string
                  description: Código de respuesta según resultado de la transacción
                - in: formData
                  name: transactionDescription
                  required: false
                  type: string
                  description: Descripcion del status del campo anterior
            responses:
                    200:
                        description: Collection successfully created
                        schema:
                          id: success
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
        data = request.form
        tm_manager = TigoMoneyManager()
        tm_manager.payment_callback(data)
        return response_with(resp.SUCCESS_200)
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/payment_providers/bancard/callback', methods=['POST'])
def bancard_callback():
    pass


@route_path_general.route('/1.0/users', methods=['POST'])
@auth_tk.login_required
def create_user():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return response_with(resp.MISSING_PARAMETERS_422)  # missing arguments
        if User.query.filter_by(username=username).first() is not None:
            return response_with(resp.EXISTING_USER_400)
        user = User(username=username)
        user.hash_password(password)
        user.create()
        return response_with(resp.SUCCESS_200, value={"username": user.username})
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/users', methods=['GET'])
@auth_tk.login_required
def get_users():
    try:
        user_schema = UserSchema(many=True, only=['username', 'active'])
        users = User.query.all()
        result, error = user_schema.dumps(users)
        return response_with(resp.SUCCESS_200, value={"users": result})
    except Exception:
        return response_with(resp.INVALID_INPUT_422)
