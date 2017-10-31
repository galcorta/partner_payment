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
def create_data():
    """Creates sample data."""
    from src.api.models.model_debt import Debt
    for i in range(7, 13):
        debt = Debt(
            id_socio=1,
            mes=str(i),
            monto=100000,
            saldo=100000,
            vencimiento=datetime.strptime('2016-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            anio='2016'
        )
        debt.create()

    for i in range(1, 13):
        debt = Debt(
            id_socio=1,
            mes=str(i),
            monto=130000,
            saldo=130000,
            vencimiento=datetime.strptime('2017-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            anio='2017'
        )
        debt.create()


@manager.command
def create_data_demo():
    """Creates sample data."""
    from src.api.models.model_debt import Debt
    for i in range(11, 13):
        debt = Debt(
            id_socio=2,
            mes=str(i),
            monto=120000,
            saldo=120000,
            vencimiento=datetime.strptime('2016-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            anio='2016'
        )
        debt.create()

    for i in range(1, 13):
        debt = Debt(
            id_socio=2,
            mes=str(i),
            monto=150000,
            saldo=150000,
            vencimiento=datetime.strptime('2017-' + str(i).zfill(2) + '-05T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            anio='2017'
        )
        debt.create()


@manager.command
def create_admin():
    """Creates the admin user."""
    from src.api.models.model_partner import Partner
    db.session.add(Partner(
        nro_socio='1111',
        nombre='Carlos Perez',
        documento_identidad='1111111',
        email='juan.perez@example.com',
        password='admin'))
    db.session.commit()


@manager.command
def create_demo():
    """Creates the demo user."""
    from src.api.models.model_partner import Partner
    db.session.add(Partner(
        nro_socio='2222',
        nombre='Nelia Velazquez',
        documento_identidad='2222222',
        email='nelia.velazquez@example.com',
        password='demo'))
    db.session.commit()

if __name__ == '__main__':
    manager.run()
