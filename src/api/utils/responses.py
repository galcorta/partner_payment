#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import make_response, jsonify
from enum import Enum
from ...api import app


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
    "code": "badRequest",
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
    "message": "Server error"
}

NOT_FOUND_HANDLER_404 = {
    "http_code": 404,
    "code": "notFound",
    "message": "There are no such handler"
}

SUCCESS_200 = {
    'http_code': 200,
    'code': 'success'
}


# Special
ACCESS_TOKEN_200 = {
    'http_code': 200,
    'code': 'success',
    'message': 'Token generado exitosamente.',
    'token': ''
}

EXISTING_USER_400 = {
    "http_code": 400,
    "code": "existingUser",
    "message": "Nombre de usuario ya existente."
}

INVALID_CREDENTIALS_401 = {
    "http_code": 401,
    "code": "invalidCredentials",
    "message": "Credenciales inválidas."
}

INVALID_TOKEN_403 = {
    "http_code": 403,
    "code": "invalidToken",
    "message": "Token inválido o expirado."
}

INVALID_PARTNER_422 = {
    "http_code": 422,
    "code": "invalidInput",
    "message": "El número de cédula proveído no existe en el sistema."
}

INVALID_PAYMENT_PROVIDER_422 = {
    "http_code": 422,
    "code": "invalidInput",
    "message": "El proveedor de pago no existe en el sistema o no esta habilitado."
}

CUSTOM_SERVER_ERROR_500 = {
    "http_code": 500,
    "code": "serverError"
}


def response_with(response, value=None, message=None, error=None, headers={}, pagination=None):
    result = {}
    if value is not None:
        result.update(value)

    if response.get('message', None) is not None:
        result.update({'message': response['message']})

    result.update({'code': response['code']})

    if error is not None:
        result.update({'errors': error})

    if pagination is not None:
        result.update({'pagination': pagination})

    headers.update({'Access-Control-Allow-Origin': '*'})
    headers.update({'server': 'Payment API'})

    return make_response(jsonify(result), response['http_code'], headers)


class IRStatus(Enum):
    success = 1
    fail = 2
    fail_400 = 3
    fail_500 = 4


class InternalResponse(object):

    def __init__(self, status=IRStatus.success, message=None, value=None):
        self.status = status
        self.message = message or (status == 'success' and 'Operación exitosa!' or None)
        self.value = value
        if not status == IRStatus.success and self.message:
            app.logger.info(self.message)
