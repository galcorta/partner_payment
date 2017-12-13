# -*- coding: utf-8 -*-
from ...api import db


# Models
class PaymentProvider(db.Model):
    __tablename__ = "PaymentProvider"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    active = db.Column(db.Boolean, default=True)
    configurations = db.relationship("PaymentProviderConfiguration", backref="payment_provider")
    endpoints = db.relationship("PaymentProviderEndpoint", backref="payment_provider")

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def get_config_by_name(self, config_name):
        return [config.value for config in self.configurations
                if config.name == config_name][0]

    def get_endpoint_by_name(self, endpoint_name):
        return [endpoint.uri for endpoint in self.endpoints
                if endpoint.name == endpoint_name][0]

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PaymentProviderConfiguration(db.Model):
    __tablename__ = "PaymentProviderConfiguration"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_provider_id = db.Column(db.Integer, db.ForeignKey('PaymentProvider.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    value = db.Column(db.String)
    description = db.Column(db.String)
    active = db.Column(db.Boolean, default=True)

    def __init__(self, payment_provider_id, name, value, description):
        self.payment_provider_id = payment_provider_id
        self.name = name
        self.value = value
        self.description = description

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PaymentProviderEndpoint(db.Model):
    __tablename__ = "PaymentProviderEndpoint"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_provider_id = db.Column(db.Integer, db.ForeignKey('PaymentProvider.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    uri = db.Column(db.String)
    read_to = db.Column(db.Integer)
    connect_to = db.Column(db.Integer)
    description = db.Column(db.String)
    active = db.Column(db.Boolean, default=True)

    def __init__(self, payment_provider_id, name, uri, read_to, connect_to, description):
        self.payment_provider_id = payment_provider_id
        self.name = name
        self.uri = uri
        self.read_to = read_to
        self.connect_to = connect_to
        self.description = description

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PaymentProviderOperation(db.Model):
    __tablename__ = "PaymentProviderOperation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('CollectionTransaction.id'), nullable=False)
    payment_provider_id = db.Column(db.Integer, db.ForeignKey('PaymentProvider.id'), nullable=False)
    method = db.Column(db.String)
    content_type = db.Column(db.String)
    authorization = db.Column(db.String)
    status_code = db.Column(db.Integer)
    content = db.Column(db.Text)
    direction = db.Column(db.Enum("sended", "received", name='tm_operation_direction'))
    parent_id = db.Column(db.Integer, db.ForeignKey('PaymentProviderOperation.id'))
    operation_type = db.Column(db.Enum("request", "response", name='tm_operation_type'))
    create_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    active = db.Column(db.Boolean, default=True)

    def __init__(self, transaction_id, payment_provider_id, operation_type, direction,
                 content_type, content, method=None, authorization=None, status_code=None, parent_id=None):
        self.transaction_id = transaction_id
        self.payment_provider_id = payment_provider_id
        self.method = method
        self.content_type = content_type
        self.authorization = authorization
        self.status_code = status_code
        self.operation_type = operation_type
        self.content = content
        self.direction = direction
        self.parent_id = parent_id

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
