# -*- coding: utf-8 -*-

from ...api import app, db, bcrypt
from marshmallow_sqlalchemy import ModelSchema
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "apiusr01"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    write_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    create_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    active = db.Column(db.Boolean, default=True)

    def hash_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def verify_password(self, password):
        return bcrypt.check_password_hash(
            self.password_hash, password
        )

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)

        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = User
        sqla_session = db.session
