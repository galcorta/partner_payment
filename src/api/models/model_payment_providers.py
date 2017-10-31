#!/usr/bin/python
# -*- coding: utf-8 -*-

from ...api import db
from marshmallow import fields, Schema


"""
Tigo models shema
"""


class MasterMerchant(Schema):
    account = db.Column(db.String)
    pin = db.Column(db.String)
    id = db.Column(db.String)


class Subscriber(Schema):
    account = db.Column(db.String)
    country_code = db.Column(db.String)
    country = db.Column(db.String)
    email_id = db.Column(db.String)


class Payment(Schema):
    amount = db.Column(db.String)
    currency_code = db.Column(db.String)
    tax = db.Column(db.String)
    fee = db.Column(db.String)
