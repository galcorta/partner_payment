# -*- coding: utf-8 -*-

from ..utils.responses import response_with
from ..utils import responses as resp
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth
from flask import g
from ..models.collection import CollectionEntity


auth = HTTPBasicAuth()
auth_tk = HTTPTokenAuth('Bearer')


@auth.verify_password
def verify_password(username, password):
    if username and password:
        # try to authenticate with username/password
        entity = CollectionEntity.query.filter_by(username=username).first()
        if not entity or not entity.verify_password(password):
            return False
        g.entity = entity
        return True
    else:
        return False


@auth_tk.verify_token
def verify_token(token):
    if token:
        entity = CollectionEntity.verify_auth_token(token)
        if entity:
            g.entity = entity
            return True
        else:
            return False
    else:
        return False


@auth.error_handler
def auth_error():
    return response_with(resp.INVALID_CREDENTIALS_401)


@auth_tk.error_handler
def auth_error():
    return response_with(resp.INVALID_TOKEN_403)
