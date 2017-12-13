#!/usr/bin/env python
# -*- coding: utf-8 -*-

#################
#### imports ####
#################

import os
from flask import Flask
from flask import jsonify
from flask_swagger import swagger
from .utils.database import db
from .utils.crypt import bcrypt
from flask_cors import CORS
from flask_migrate import Migrate

import logging
import logging.config
from .utils.logging_manager import LoggerConfig

################
#### config ####
################

app = Flask(__name__)

CORS(app)

app_settings = os.getenv('APP_SETTINGS', 'src.api.utils.config.ProductionConfig')
app.config.from_object(app_settings)


################
### logging ####
################

app.logger  # initialise logger
logging.config.dictConfig(LoggerConfig.dictConfig)

app.logger.info("Inicia la app")

####################
#### extensions ####
####################

bcrypt.init_app(app)

db.init_app(app)

migrate = Migrate(app, db)


###################
### blueprints ####
###################
from .routes.routes_general import route_path_general
app.register_blueprint(route_path_general, url_prefix='/api')


###################################
### global http configurations ####
###################################
from .utils.responses import response_with, BAD_REQUEST_400, SERVER_ERROR_404, SERVER_ERROR_500, \
    NOT_FOUND_HANDLER_404

@app.after_request
def add_header(response):
    return response


@app.errorhandler(400)
def bad_request(e):
    logging.error(e)
    return response_with(BAD_REQUEST_400)


@app.errorhandler(500)
def server_error(e):
    logging.error(e)
    app.logger.error(e)
    return response_with(SERVER_ERROR_500)


@app.errorhandler(404)
def not_found(e):
    logging.error(e)
    return response_with(NOT_FOUND_HANDLER_404)


###################
### spec route ####
###################

@app.route("/api/1.0/spec")
def spec():
    swag = swagger(app, prefix='/api/1.0')
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Partner payment API"
    swag['info']['description'] = "REST API para pago de cuotas de socios."
    app.logger.info('Info - Partner payment API')
    return jsonify(swag)


from .models import *


################
### logging ####
################

# logging.basicConfig(stream=sys.stdout,
#                     format='%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s',
#                     level=logging.DEBUG)
