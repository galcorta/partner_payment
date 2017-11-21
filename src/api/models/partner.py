# -*- coding: utf-8 -*-

from ...api import app, db, bcrypt
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, Schema


# Models
class Partner(db.Model):
    __tablename__ = 'assoc01'

    id = db.Column('id_socio', db.Integer, primary_key=True, autoincrement=True)
    nro_socio = db.Column(db.Integer)
    fecha_ingreso = db.Column(db.Date)
    empresa = db.Column(db.Text)
    nombre = db.Column(db.String(255))
    categoria = db.Column(db.String(255))
    estado = db.Column(db.String(255))
    documento_identidad = db.Column(db.String(255))
    identidad = db.Column(db.String(255))
    sexo = db.Column(db.String(255))
    estado_civil = db.Column(db.String(255))
    fecha_nacimiento = db.Column(db.DateTime)
    edad_actual = db.Column(db.String(255))
    direccion = db.Column(db.String(255))
    departamento = db.Column(db.String(255))
    ciudad = db.Column(db.String(255))
    barrio = db.Column(db.String(255))
    direccion_laboral = db.Column(db.String(255))
    telefono = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    celular = db.Column(db.String(255))
    foto_socio = db.Column(db.String(255))
    comentario = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, nro_socio, nombre, documento_identidad, email, password):
        self.nro_socio = nro_socio
        self.nombre = nombre
        self.documento_identidad = documento_identidad
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode('utf-8')

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def verify_password(self, password):
        first3_name = self.nombre.lower().strip()[:3]
        last3_ci = self.documento_identidad.strip()[-3:]
        correct_password = first3_name + last3_ci
        return password.lower() == correct_password

    def __repr__(self):
        return '<Partner {0}>'.format(self.nombre)


class PartnerCollection(db.Model):
    __tablename__ = "ascob01"

    id = db.Column('id_cobro', db.Integer, primary_key=True, autoincrement=True)
    id_socio = db.Column(db.Integer, db.ForeignKey('assoc01.id_socio'), nullable=False)
    fecha = db.Column(db.Date)
    nro_socio = db.Column(db.Integer)
    categoria = db.Column(db.String(50))
    anno = db.Column(db.Integer)
    monto_cobrado = db.Column(db.Integer)
    nro_recibo = db.Column(db.Integer)
    estado = db.Column(db.Text)
    nota = db.Column(db.Text)
    details = db.relationship('PartnerCollectionDetail', backref='collection',
                                lazy='dynamic')
    collection_ways = db.relationship('PartnerCollectionWay', backref='collection',
                                lazy='dynamic')

    def __init__(self, id_socio, fecha, nro_socio, categoria, anno, monto_cobrado, nro_recibo, estado, nota,
                 details, collection_ways):
        self.id_socio = id_socio
        self.fecha = fecha
        self.nro_socio = nro_socio
        self.categoria = categoria
        self.anno = anno
        self.monto_cobrado = monto_cobrado
        self.nro_recibo = nro_recibo
        self.estado = estado
        self.nota = nota
        self.details = details
        self.collection_ways = collection_ways

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Collection {0}>'.format(self.efectivo)

    @staticmethod
    def create_collection(debts, payment_provider, trx_id):
        partner = Partner.query.get(debts[0].id_socio)
        created_date = db.func.now()
        total_amount = 0
        collection_detail_list = []
        for debt in debts:
            total_amount += debt.amount
            collection_detail_list.append(PartnerCollectionDetail(id_cuota=debt.id,
                                                                  monto=debt.amount,
                                                                  fecha=created_date))
            debt.saldo_x_cobrar -= debt.amount

        collection_way_list = [PartnerCollectionWay(partner.id, partner.nro_socio, created_date, payment_provider,
                                                    total_amount, trx_id)]
        collection = PartnerCollection(
            id_socio=partner.id,
            fecha=created_date,
            nro_socio=partner.nro_socio,
            categoria=None,
            anno=None,
            monto_cobrado=total_amount,
            nro_recibo=None,
            estado=None,
            nota=None,
            details=collection_detail_list,
            collection_ways=collection_way_list
        ).create()

        db.session.commit()

        return collection


class PartnerCollectionDetail(db.Model):
    __tablename__ = "ascbd01"

    id = db.Column('id_cobro_detalle', db.Integer, primary_key=True, autoincrement=True)
    id_cobro = db.Column(db.Integer, db.ForeignKey('ascob01.id_cobro'), nullable=False)
    id_cuota = db.Column(db.Integer)
    monto = db.Column(db.Integer)
    fecha = db.Column(db.Date)

    def __init__(self, id_cuota, monto, fecha):
        self.id_cuota = id_cuota
        self.monto = monto
        self.fecha = fecha


class PartnerCollectionWay(db.Model):
    __tablename__ = "astpc01"

    id = db.Column('id_tipo_cobro', db.Integer, primary_key=True, autoincrement=True)
    id_cobro = db.Column(db.Integer, db.ForeignKey('ascob01.id_cobro'), nullable=False)
    id_socio = db.Column(db.Integer)
    nro_socio = db.Column(db.Integer)
    fecha = db.Column(db.Date)
    tipo = db.Column(db.String(50))
    monto = db.Column(db.Integer)
    id_transaccion = db.Column(db.Integer, db.ForeignKey('coltrx01.id'), nullable=False)

    def __init__(self, id_socio, nro_socio, fecha, tipo, monto, id_transaccion):
        self.id_socio = id_socio
        self.nro_socio = nro_socio
        self.fecha = fecha
        self.tipo = tipo,
        self.monto = monto
        self.id_transaccion = id_transaccion

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<CollectionWay {0}>'.format(self.id_tipo_cobro)


# Schemas
class PartnerSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Partner
        sqla_session = db.session


class PartnerLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class PartnerLoginResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    username = fields.String()
    access_token = fields.String()
