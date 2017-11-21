# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    TESTING = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = 'postgresql://macrosys:macrosys@localhost:5432/macrosys'
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')

class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    SQLALCHEMY_ECHO = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    SQLALCHEMY_DATABASE_URI = 'postgresql://macrosys:macrosys@localhost:5432/macrosys'
