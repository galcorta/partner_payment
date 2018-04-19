# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import g
import json

from ..controllers.tigomoney import TigoMoneyManager
from ..controllers.bancard_vpos import BancardVposManager
from ..utils.responses import response_with
from ..utils import responses as resp
from ..models.collection import CollectionEntity, CollectionEntitySchema, CollectionTransaction, \
    CollectionTransactionSchema
from ..utils.auth import auth, auth_tk
from ..models.factusys import Partner, PartnerLoginSchema, PartnerLoginResponseSchema, \
    PartnerDebt, PartnerDebtSchema, PartnerCollection
from ..controllers.collection import CollectionController
from ...api import app, db
from ..controllers.factusys import FactusysManager

route_path_general = Blueprint("route_path_general", __name__)


@route_path_general.route('/1.0/token', methods=['POST'])
@auth.login_required
def get_auth_token():
    """
    Token Generation
    ---
    parameters:
        - in: header
          name: authorization
          type: string
          required: true
    responses:
        200:
            description: Success token generation
            schema:
                id: succesTokenGeneration
                properties:
                    code:
                        type: string
                    message:
                        type: string
                    token:
                        type: string
        401:
            description: Invalid credentials
            schema:
                id: invalidCredentials
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
        token = g.entity.generate_auth_token(600)
        return response_with(resp.SUCCESS_200,
                             value={'token': token.decode('ascii')},
                             message="Token generado exitosamente.")
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.SERVER_ERROR_500)


#  Solo se utiliza desde la web
@route_path_general.route('/1.0/partners/authenticate', methods=['POST'])
@auth.login_required
def partner_authenticate():
    # """
    #     Partner login
    #     ---
    #     parameters:
    #         - in: body
    #           name: body
    #           description: Login of the partner
    #           schema:
    #             id: partnerLogin
    #             required:
    #                 - username
    #                 - password
    #             properties:
    #                 username:
    #                     type: string
    #                     description: Username of the partner
    #                 password:
    #                     type: string
    #                     description: Password of the partner
    #
    #     responses:
    #             200:
    #                 description: Partner successfully login
    #                 schema:
    #                   id: partnerLoginSuccess
    #                   properties:
    #                     code:
    #                       type: string
    #                     message:
    #                       type: string
    #                     token:
    #                       type: string
    #                     user:
    #                         id: partner
    #                         properties:
    #                             name:
    #                                 type: string
    #                             username:
    #                                 type: string
    #
    #             403:
    #                 description: Invalid credentials
    #                 schema:
    #                     id: invalidCredentials
    #                     properties:
    #                         code:
    #                             type: string
    #                         message:
    #                             type: string
    #     """
    try:
        data = request.get_json()
        partner_schema_login = PartnerLoginSchema()
        partner_login, error = partner_schema_login.load(data)
        partner = Partner.query.filter_by(documento_identidad=partner_login['username']).one_or_none()
        if not partner:
            partner = Partner.query.filter(Partner.documento_identidad ==
                                           Partner.get_ruc_from_ci(data['username'])).one_or_none()
        if partner and partner.nombre:
            # if partner.verify_password(partner_login['password']):
            token = g.entity.generate_auth_token(600)
            partner.name = partner.nombre
            partner.username = partner.documento_identidad
            partner.state = partner.estadocliente
            login_response_schema = PartnerLoginResponseSchema()
            result = login_response_schema.dump(partner).data
            return response_with(resp.SUCCESS_200,
                                 value={'user': result, 'token': token},
                                 message='Operación exitosa.')
        else:
            return response_with(resp.INVALID_CREDENTIALS_401)
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.SERVER_ERROR_500)


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
                      id: debtList
                      properties:
                        code:
                            type: string
                        message:
                            type: string
                        debts:
                            type: array
                            items:
                                schema:
                                    id: debt
                                    properties:
                                        id:
                                            type: integer
                                        saldo:
                                            type: integer
                                        fecha_vencimiento:
                                            type: string
        """
    try:
        partner = Partner.query.filter(Partner.documento_identidad == username).all()
        if not partner:
            partner = Partner.query.filter(Partner.documento_identidad == Partner.get_ruc_from_ci(username)).all()

        if partner:
            partner = partner[0]

            pending_collections = CollectionTransaction.query.filter(CollectionTransaction.partner_id == partner.id,
                                                                     CollectionTransaction.status == 'pending').all()
            pending_debt_ids = []
            if pending_collections:
                for item in pending_collections:
                    data = json.loads(item.data)
                    pending_debt_ids.extend([d['id'] for d in data['debts']])

            if g.entity.username == 'webportal':
                query = PartnerDebt.query.filter(PartnerDebt.id_cliente == partner.id,
                                                 PartnerDebt.saldo > 0).order_by(PartnerDebt.fecha_vencimiento)
                fetched = query.all()
                for debt in fetched:
                    debt.pending = True if debt.id in pending_debt_ids else False

            else:
                query = PartnerDebt.query.filter(PartnerDebt.id_cliente == partner.id,
                                                 PartnerDebt.saldo > 0,
                                                 PartnerDebt.id.notin_(pending_debt_ids))\
                    .order_by(PartnerDebt.fecha_vencimiento)
                fetched = query.all()[0:(g.entity.username == 'pronet' and 5 or 100)]

            debt_schema = PartnerDebtSchema(many=True, only=['id', 'saldo', 'fecha_vencimiento', 'pending'])
            debts, error = debt_schema.dump(fetched)
            return response_with(resp.SUCCESS_200,
                                 value={"name": partner.nombre, "debts": debts},
                                 message='Operación exitosa.')
        else:
            return response_with(resp.INVALID_PARTNER_422)
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.SERVER_ERROR_500)


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
                id: debtCollect
                required:
                  - payment_provider_data
                  - debts
                properties:
                    debts:
                        type: array
                        description: Listado de cuotas cobradas
                        items:
                            schema:
                                id: debtCollect
                                properties:
                                    id:
                                        type: integer
                                    amount:
                                        type: integer
                    payment_provider_data:
                        type: object
                        description: Datos referentes a la entidad cobradora.
                        schema:
                            id: paymentProviderData
                            required:
                              - name
                            properties:
                                name:
                                    type: string
                                voucher:
                                    type: string
                                payment_provider_data:
                                    type: object

        responses:
                200:
                    description: Collection successfully created
                    schema:
                      id: collectionCreated
                      properties:
                        code:
                          type: string
                        message:
                          type: string
                        transaction_id:
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
        if data:
            collection_controller = CollectionController(data)
            return collection_controller.collect()
        else:
            return response_with(resp.BAD_REQUEST_400)
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/1.0/partners/collection/<string:transaction_id>', methods=['GET'])
@auth_tk.login_required
def get_collection(transaction_id):
    try:
        collection_trx = CollectionTransaction.query.filter_by(display_id=transaction_id).one_or_none()
        if collection_trx:
            col_trx_schema = CollectionTransactionSchema(only=['display_id', 'amount', 'status'])
            coll_trx, error = col_trx_schema.dump(collection_trx)
            if not error:
                return response_with(resp.SUCCESS_200, value={"collection": coll_trx})
            else:
                return response_with(resp.SERVER_ERROR_500)
        else:
            return response_with(resp.INVALID_INPUT_422)
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/1.0/partners/collection/<string:voucher>', methods=['PUT'])
@auth_tk.login_required
def cancel_partner_collection(voucher):
    try:
        # data = request.get_json()
        collection_controller = CollectionController(voucher)
        return collection_controller.cancel()
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/1.0/payment-providers/tigo-money/callback', methods=['POST'])
def tigo_callback():
    # """
    # Tigo Callback
    # ---
    # parameters:
    #     - in: formData
    #       name: transactionStatus
    #       required: true
    #       type: string
    #       description: Transaction status success/fail
    #     - in: formData
    #       name: merchantTransactionId
    #       required: false
    #       type: string
    #       description: Identificador proveido por el merchant
    #     - in: formData
    #       name: mfsTransactionId
    #       required: false
    #       type: string
    #       description: ID de transacción generado en la plataforma de Tigo Money
    #     - in: formData
    #       name: accessToken
    #       required: false
    #       type: string
    #       description: Token utilizado
    #     - in: formData
    #       name: transactionCode
    #       required: false
    #       type: string
    #       description: Código de respuesta según resultado de la transacción
    #     - in: formData
    #       name: transactionDescription
    #       required: false
    #       type: string
    #       description: Descripcion del status del campo anterior
    # responses:
    #         200:
    #             description: Collection successfully created
    #             schema:
    #               id: success
    #               properties:
    #                 code:
    #                   type: string
    #                 message:
    #                   type: string
    #         422:
    #             description: Invalid input arguments
    #             schema:
    #                 id: invalidInput
    #                 properties:
    #                     code:
    #                         type: string
    #                     message:
    #                         type: string
    # """
    try:
        data = request.form
        tm_manager = TigoMoneyManager()
        return tm_manager.payment_callback(data)
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/1.0/payment-providers/bancard-vpos/callback', methods=['POST'])
def bancard_callback():
    try:
        data = request.get_json()
        bancard_vpos_manager = BancardVposManager()
        return bancard_vpos_manager.payment_callback(data)
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/users', methods=['POST'])
@auth_tk.login_required
def create_collection_entity():
    try:
        name = request.json.get('username')
        username = request.json.get('username')
        password = request.json.get('password')
        if name is None or username is None or password is None:
            return response_with(resp.MISSING_PARAMETERS_422)
        if CollectionEntity.query.filter_by(username=username).one_or_none() is not None:
            return response_with(resp.EXISTING_USER_400)
        if CollectionEntity.query.filter_by(name=name).one_or_none() is not None:
            return response_with(resp.EXISTING_USER_400)
        entity = CollectionEntity(name=name, username=username)
        entity.hash_password(password)
        entity.create()
        return response_with(resp.SUCCESS_200, value={"username": entity.username})
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/users', methods=['GET'])
@auth_tk.login_required
def get_collection_entity():
    try:
        entity_schema = CollectionEntitySchema(many=True, only=['username', 'active'])
        entities = CollectionEntity.query.all()
        result, error = entity_schema.dumps(entities)
        return response_with(resp.SUCCESS_200, value={"entities": result})
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/users', methods=['PUT'])
@auth_tk.login_required
def update_collection_entity():
    try:
        data = request.get_json()
        collection_entity_schema = CollectionEntitySchema(only=['id', 'password_hash'])
        entity, error = collection_entity_schema.load(data)
        if entity:
            entity.hash_password(entity.password_hash)
            db.session.commit()
            collection_entity_schema_full = CollectionEntitySchema(exclude=['password_hash'])
            entity_json, error = collection_entity_schema_full.dump(entity)
            if entity_json:
                return response_with(resp.SUCCESS_200, value={"collection_entity": entity_json})
            else:
                return response_with(resp.MISSING_PARAMETERS_422)
        else:
            return response_with(resp.MISSING_PARAMETERS_422)
    except Exception:
        return response_with(resp.INVALID_INPUT_422)


@route_path_general.route('/1.0/partners/register', methods=['POST'])
@auth.login_required
def create_partner():
    try:
        data = request.get_json()
        factusys_manager = FactusysManager()
        return factusys_manager.create_partner(data)
    except Exception, e:
        app.logger.error(str(e))
        return response_with(resp.SERVER_ERROR_500, message='Ha ocurrido un inconveniente al realizar la operacion. '
                                                            'Por favor vuelva a intentar, si el inconveniente persiste '
                                                            'comuniquese con el Club.')


@route_path_general.route('/1.0/cities', methods=['GET'])
@auth.login_required
def get_cities():
    try:
        factusys_manager = FactusysManager()
        result = factusys_manager.get_cities()
        return response_with(resp.SUCCESS_200, value={"cities": result})
    except Exception:
        return response_with(resp.SERVER_ERROR_500)


@route_path_general.route('/1.0/departments', methods=['GET'])
@auth.login_required
def get_departments():
    try:
        factusys_manager = FactusysManager()
        result = factusys_manager.get_departments()
        return response_with(resp.SUCCESS_200, value={"departments": result})
    except Exception:
        return response_with(resp.SERVER_ERROR_500)


# @route_path_general.route('/1.0/collection/migration', methods=['POST'])
# def collection_migration():
#     try:
#         MigPagosElectronicos.run_migration()
#         return response_with(resp.SUCCESS_200)
#     except Exception, e:
#         app.logger.error(str(e))
#         return response_with(resp.SERVER_ERROR_500)

@route_path_general.route('/1.0/categories', methods=['GET'])
@auth.login_required
def get_categories():
    try:
        factusys_manager = FactusysManager()
        result = factusys_manager.get_categories()
        return response_with(resp.SUCCESS_200, value={"categories": result})
    except Exception:
        return response_with(resp.SERVER_ERROR_500)


# @route_path_general.route('/1.0/collection/migration', methods=['POST'])
# def collection_migration():
#     try:
#         MigPagosElectronicos.run_migration()
#         return response_with(resp.SUCCESS_200)
#     except Exception, e:
#         app.logger.error(str(e))
#         return response_with(resp.SERVER_ERROR_500)