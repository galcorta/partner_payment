#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime
from src.api import app, db

# migrate = Migrate(app, db)
manager = Manager(app)
# manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_data_demo():
    """Creates sample data."""
    from src.api.models.partner import Partner
    from src.api.models.partner_debt import PartnerDebt
    from src.api.models.payment_provider import PaymentProvider, PaymentProviderConfiguration, PaymentProviderEndpoint

    db.session.add(Partner(
        nro_socio='1111',
        nombre='Carlos Perez',
        documento_identidad='1111111',
        email='juan.perez@example.com',
        password='admin'))
    db.session.commit()

    db.session.add(Partner(
        nro_socio='2222',
        nombre='Nelia Velazquez',
        documento_identidad='2222222',
        email='nelia.velazquez@example.com',
        password='demo'))
    db.session.commit()

    for i in range(11, 13):
        debt = PartnerDebt(
            id_socio=2,
            mes=str(i),
            monto=12000,
            saldo=12000,
            vencimiento=datetime.strptime('2016-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            anio='2016'
        )
        debt.create()

    for i in range(1, 13):
        debt = PartnerDebt(
            id_socio=2,
            mes=str(i),
            monto=15000,
            saldo=15000,
            vencimiento=datetime.strptime('2017-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            anio='2017'
        )
        debt.create()

    for i in range(7, 13):
        debt = PartnerDebt(
            id_socio=1,
            mes=str(i),
            monto=10000,
            saldo=10000,
            vencimiento=datetime.strptime('2016-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            anio='2016'
        )
        debt.create()

    for i in range(1, 13):
        debt = PartnerDebt(
            id_socio=1,
            mes=str(i),
            monto=13000,
            saldo=13000,
            vencimiento=datetime.strptime('2017-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            anio='2017'
        )
        debt.create()

    tigo = PaymentProvider(
        name='tigo_money',
        description='Tigo Money'
    ).create()

    bancard = PaymentProvider(
        name='bancard_vpos',
        description='Bancard VPOS'
    ).create()

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='TM_API_KEY',
        value='01R3ePn0AWLUAQ7aQh2weTDz52dYvZm3',
        description=''
    ).create()

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='TM_SECRET',
        value='KRrH5B8dvgZzk409',
        description=''
    ).create()

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='TM_REDIRECT_URI',
        value='https://test.api.tigo.com/v1/tigo/diagnostics/callback',
        description=''
    ).create()

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='TM_CALLBACK_URI',
        value='https://test.api.tigo.com/v1/tigo/diagnostics/callback',
        description=''
    ).create()

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='TM_AGENT_MSISDN',
        value='0981141971',
        description=''
    ).create()

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='TM_AGENT_PIN',
        value='1234',
        description=''
    ).create()

    PaymentProviderEndpoint(
        payment_provider_id=tigo.id,
        name='TM_TOKEN_URI',
        uri='https://securesandbox.tigo.com/v1/oauth/mfs/payments/tokens',
        read_to=10,
        connect_to=60,
        description=''
    ).create()

    PaymentProviderEndpoint(
        payment_provider_id=tigo.id,
        name='TM_PAYMENT_URI',
        uri='https://securesandbox.tigo.com/v2/tigo/mfs/payments/authorizations',
        read_to=10,
        connect_to=60,
        description=''
    ).create()


if __name__ == '__main__':
    manager.run()
