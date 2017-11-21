# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, make_response, session
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth
from flask import g
from ..models.user import User


auth = HTTPBasicAuth()
auth_tk = HTTPTokenAuth('Bearer')


@auth.verify_password
def verify_password(username, password):
    if username and password:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return False
        g.user = user
        return True
    else:
        return False


@auth_tk.verify_token
def verify_token(token):
    if token:
        user = User.verify_auth_token(token)
        if user:
            g.user = user
            return True
        else:
            return False
    else:
        return False
