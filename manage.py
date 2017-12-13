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
    from src.api.models.payment_provider import PaymentProvider, PaymentProviderConfiguration, \
        PaymentProviderEndpoint, PaymentProviderOperation
    from src.api.models.collection import CollectionTransaction, CollectionEntity
    """Drops the db tables."""
    # db.drop_all()
    db.metadata.drop_all(db.engine, tables=[
        PaymentProviderOperation.__table__,
        PaymentProviderConfiguration.__table__,
        PaymentProviderEndpoint.__table__,
        PaymentProvider.__table__,
        CollectionTransaction.__table__,
        CollectionEntity.__table__,
    ])


@manager.command
def create_debts_demo():
    from src.api.models.factusys import PartnerDebt
    for i in range(11, 13):
        debt = PartnerDebt(
            id_libroventa=1,
            monto=12000,
            estado='Pendiente',
            fecha_vencimiento=datetime.strptime('2017-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            fecha_financiacion=datetime.utcnow(),
            nro_cuota=i,
            saldo=12000,
            id_cliente=1,
            cod_deuda_cliente=0,
            pagare=False
        )
        debt.create()

    for i in range(1, 13):
        debt = PartnerDebt(
            id_libroventa=1,
            monto=13000,
            estado='Pendiente',
            fecha_vencimiento=datetime.strptime('2018-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            fecha_financiacion=datetime.utcnow(),
            nro_cuota=i,
            saldo=13000,
            id_cliente=1,
            cod_deuda_cliente=0,
            pagare=False
        )
        debt.create()

    for i in range(7, 13):
        debt = PartnerDebt(
            id_libroventa=1,
            monto=10000,
            estado='Pendiente',
            fecha_vencimiento=datetime.strptime('2017-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            fecha_financiacion=datetime.utcnow(),
            nro_cuota=i,
            saldo=10000,
            id_cliente=2,
            cod_deuda_cliente=0,
            pagare=False
        )
        debt.create()

    for i in range(1, 13):
        debt = PartnerDebt(
            id_libroventa=1,
            monto=11000,
            estado='Pendiente',
            fecha_vencimiento=datetime.strptime('2018-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            fecha_financiacion=datetime.utcnow(),
            nro_cuota=i,
            saldo=11000,
            id_cliente=2,
            cod_deuda_cliente=0,
            pagare=False
        )
        debt.create()


@manager.command
def create_data_demo():
    """Creates sample data."""

    from src.api.models.payment_provider import PaymentProvider, PaymentProviderConfiguration, PaymentProviderEndpoint

    # db.session.add(Partner(
    #     nro_socio='1111',
    #     nombre='Carlos Perez',
    #     documento_identidad='1111111',
    #     email='juan.perez@example.com',
    #     password='admin'))
    # db.session.commit()
    #
    # db.session.add(Partner(
    #     nro_socio='2222',
    #     nombre='Nelia Velazquez',
    #     documento_identidad='2222222',
    #     email='nelia.velazquez@example.com',
    #     password='demo'))
    # db.session.commit()

    tigo = PaymentProvider(
        name='tigo_money',
        description='Tigo Money'
    ).create()

    bancard = PaymentProvider(
        name='bancard_vpos',
        description='Bancard VPOS'
    ).create()

    red_cobranza = PaymentProvider(
        name='red_cobranza',
        description='Red de cobranzas'
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

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='TIPO_COMPROBANTE',
        value='TIGO',
        description=''
    ).create()

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='CCOSTO',
        value='1.00',
        description=''
    ).create()

    PaymentProviderConfiguration(
        payment_provider_id=tigo.id,
        name='CAJA',
        value='001',
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

    PaymentProviderEndpoint(
        payment_provider_id=tigo.id,
        name='TM_REDIRECT_URI',
        uri='http://www.leantic.ga:4200/redirect/tigo-money',
        read_to=10,
        connect_to=60,
        description=''
    ).create()

    PaymentProviderEndpoint(
        payment_provider_id=tigo.id,
        name='TM_CALLBACK_URI',
        uri='http://api.leantic.ga:8001/api/1.0/payment-providers/tigo-money/callback',
        read_to=10,
        connect_to=60,
        description=''
    ).create()


if __name__ == '__main__':
    manager.run()
