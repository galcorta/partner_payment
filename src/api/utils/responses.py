#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import make_response, jsonify

# HTTP responses
# General
INVALID_FIELD_NAME_SENT_422 = {
    "http_code": 422,
    "code": "invalidField",
    "message": "Not all field names are valid."
}

INVALID_INPUT_422 = {
    "http_code": 422,
    "code": "invalidInput",
    "message": "Invalid input"
}

MISSING_PARAMETERS_422 = {
    "http_code": 422,
    "code": "missingParameter",
    "message": "Missing parameters."
}

BAD_REQUEST_400 = {
    "http_code": 400,
    "code": "badRequest"
}

SERVER_ERROR_404 = {
    "http_code": 404,
    "code": "notFound",
    "message": "Resource not found"
}

UNAUTHORIZED_403 = {
    "http_code": 403,
    "code": "notAuthorized",
    "message": "You are not allowed to do that."
}

SERVER_ERROR_500 = {
    "http_code": 500,
    "code": "serverError",
    "code_number": 500,
    "message": "Server error"
}

NOT_FOUND_HANDLER_404 = {
    "http_code": 404,
    "code": "notFound",
    "message": "There are no such handler"
}

SUCCESS_200 = {
    'http_code': 200,
    'code': 'success',
    'code_number': 0
}


# CUSTOM

INVALID_CREDENTIALS_401 = {
    "http_code": 401,
    "code": "invalidCredentials",
    "code_number": 1,
    "message": "Credenciales inválidas."
}

INVALID_TOKEN_403 = {
    "http_code": 403,
    "code": "invalidToken",
    "code_number": 2,
    "message": "Token inválido o expirado."
}

INVALID_PARTNER_422 = {
    "http_code": 422,
    "code": "invalidPartner",
    "code_number": 3,
    "message": "El número de cédula proveído no existe en el sistema."
}

FEE_BAD_REQUEST_400 = {
    "http_code": 400,
    "code": "badRequest",
    "code_number": 4,
    "message": "Datos de las cuotas a pagar mal informados."
}

FEE_AMOUNT_INVALID_400 = {
    "http_code": 400,
    "code": "badRequest",
    "code_number": 5,
    "message": "Monto de cuota a pagar igual o menor a cero."
}

INVALID_PAYMENT_PROVIDER_400 = {
    "http_code": 400,
    "code": "badRequest",
    "code_number": 6,
    "message": "El proveedor de pago no existe en el sistema o no está habilitado."
}

INVALID_PAYMENT_PROVIDER_NAME_400 = {
    "http_code": 400,
    "code": "badRequest",
    "code_number": 7,
    "message": "Nombre de proveedor de pago inválido!."
}

INVALID_PAYMENT_PROVIDER_DATA_400 = {
    "http_code": 400,
    "code": "badRequest",
    "code_number": 8,
    "message": "Datos del proveedor de pago inválidos!."
}

GET_TIGOMONEY_TOKEN_ERROR_500 = {
    "http_code": 500,
    "code": "serverError",
    "code_number": 9,
    "message": "Error al intentar obtener token de autorización de tigo."
}

INVALID_TRANSACTION_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 10,
    "message": "La operación que intenta anular no existe."
}

ALREADY_CANCELED_TRANSACTION_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 11,
    "message": "La operación que intenta anular ya ha sido anulada."
}

EXPIRED_TIME_TO_CANCEL_TRANSACTION_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 12,
    "message": "La operación no se puede anular, ha sido creada hace mas de un dia."
}

DISORDERED_FEE_PAYMENT_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 13,
    "message": "No puede pagar cuotas de forma desordenada dejando pendientes deudas anteriores correspondientes "
               "al mismo periodo/año"
}

FEE_CANCELED_REQUEST_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 14,
    "message": "Está intentando pagar una cuota ya abonada en su totalidad."
}

FEE_AMOUNT_EXCEEDED_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 15,
    "message": "Esta intentando pagar un monto mayor que el saldo de la cuota."
}

VOUCHER_EXISTENT_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 16,
    "message": "Ya ha enviado anteriormente una transacción con el mismo voucher."
}

CUSTOM_SERVER_ERROR_500 = {
    "http_code": 500,
    "code": "serverError",
    "code_number": 500
}


CALLBACK_BAD_REQUEST_400 = {
    "http_code": 400,
    "code": "badRequest",
    "code_number": 17,
    "message": "No se pueden procesar los datos enviados en el Body."
}

CALLBACK_INVALID_TRANSACTION_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 18,
    "message": "La operación que intenta confirmar no existe."
}

CALLBACK_INVALID_PARENT_OPERATION_422 = {
    "http_code": 422,
    "code": "validationError",
    "code_number": 19,
    "message": "No se encuentra la peticion padre que inicio la transaccion."
}

VALIDATION_ERROR_422 = {
    "http_code": 422,
    "code": "validationError"
}

EXISTING_USER_400 = {
    "http_code": 400,
    "code": "existingUser",
    "message": "Nombre de usuario ya existente."
}


def response_with(response, value=None, message=None, error=None, headers={}, pagination=None):
    result = {}
    if value is not None:
        result.update(value)

    if message:
        result.update({'message': message})
    elif response.get('message', None) is not None:
        result.update({'message': response['message']})

    result.update({'code': response['code']})
    if response.get('code_number', None) is not None:
        result.update({'code_number': response['code_number']})

    if error is not None:
        result.update({'errors': error})

    if pagination is not None:
        result.update({'pagination': pagination})

    headers.update({'Access-Control-Allow-Origin': '*'})
    headers.update({'server': 'Payment API'})

    return make_response(jsonify(result), response['http_code'], headers)
