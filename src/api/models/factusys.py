# -*- coding: utf-8 -*-

import datetime
from ...api import app, db, bcrypt
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, Schema
import sqlalchemy as sa


# Partner
class Partner(db.Model):
    __tablename__ = 'Entidades'

    id = db.Column('codigo', db.Integer, primary_key=True)
    nombre = db.Column('nombre', db.String(100))
    documento_identidad = db.Column('ruc', db.String(20))
    nro_socio = db.Column('nrosocio', db.String(50))

    def verify_password(self, password):
        first3_name = self.nombre.lower().strip()[:3]
        last3_ci = self.documento_identidad.strip()[-3:]
        correct_password = first3_name + last3_ci
        return password.lower() == correct_password

    def __repr__(self):
        return '<Partner {0}>'.format(self.nombre)


class PartnerCollection(db.Model):
    __tablename__ = "Cobros"
    __table_args__ = {'implicit_returning': False}

    id = db.Column('Idcobro', db.Integer, primary_key=True)
    id_cuota = db.Column('Idcuota', db.Integer, nullable=False, default=0)
    fecha_cobro = db.Column('Fechacobro', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    nro_detalle = db.Column('nrodetalle', db.Integer, nullable=False, default=1)
    cliente = db.Column('Cliente', db.Integer, nullable=False)
    monto = db.Column('Monto', db.Float, nullable=False)
    moneda = db.Column('Moneda', db.Integer, nullable=False, default=1)
    cotizacion = db.Column('Cotizacion', db.Float, nullable=False, default=1)
    id_forma_cobro = db.Column('IdFormaCobro', db.Integer, nullable=False, default=0)
    descripcion = db.Column('Descripcion', db.String, nullable=False)
    nro_recibo = db.Column('NroRecibo', db.String(20), nullable=False)
    comprobante = db.Column('Comprobante', db.String(6), nullable=False, default='RBO')
    comision_cobrador = db.Column('comision_cobrador', db.Float, nullable=False, default=0)
    cobrador = db.Column('Cobrador', db.Integer)
    estado = db.Column('estado', db.String(50), nullable=False, default='ACTIVO')
    cobrado = db.Column('cobrado', db.Boolean, nullable=False, default=False)
    vendedor = db.Column('vendedor', db.Integer, nullable=False, default=0)
    comision_vendedor = db.Column('comision_vendedor', db.Float, nullable=False, default=0)
    id_nota_credito = db.Column('idnotacredito', db.Integer, nullable=False, default=0)
    cod_cobro = db.Column('cod_cobro', db.Integer, nullable=False)
    cobro_por_factura = db.Column('cobroporfactura', db.Boolean, nullable=False, default=False)
    nro_tipo_comprobante = db.Column('nrotipocomprobante', db.Integer, nullable=False)
    fecha_real_cobro = db.Column('FechaRealCobro', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    user_insert = db.Column('UserInsert', db.Integer, default=1)
    fecha_insert = db.Column('FechaInsert', db.DateTime, nullable=False, default=db.func.now())
    details = db.relationship('PartnerCollectionDetail', backref='collection', lazy='dynamic')
    collection_ways = db.relationship('PartnerCollectionWay', backref='collection', lazy='dynamic')

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Collection {0}>'.format(self.amount)

    @staticmethod
    def get_count(q):
        count_q = q.statement.with_only_columns([db.func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

    @staticmethod
    def _next_cod_cobro(partner):
        query = db.session.query(PartnerCollection).filter(PartnerCollection.cliente == partner.id)
        return PartnerCollection.get_count(query) + 1

    @staticmethod
    def _next_nrotipocomprobante(partner, tipo_comprobante):
        query = db.session.query(PartnerCollection).filter(PartnerCollection.cliente == partner.id,
                                                           PartnerCollection.comprobante == tipo_comprobante)
        return PartnerCollection.get_count(query) + 1

    @staticmethod
    def create_collection(debts, payment_provider, collection_trx):
        partner = Partner.query.get(debts[0].id_cliente)
        # created_date = db.func.now()
        total_amount = 0
        collection_detail_list = []
        for debt in debts:
            total_amount += debt.amount
            collection_detail_list.append(PartnerCollectionDetail(id_cuota=debt.id,
                                                                  monto=debt.amount,
                                                                  monto_monefactura=debt.amount))
            debt.saldo -= debt.amount
            debt.estado = 'Cobrado'

        tipo_comprobante = payment_provider.get_config_by_name('TIPO_COMPROBANTE')
        nro_tipo_comprobante = PartnerCollection\
            ._next_nrotipocomprobante(partner, payment_provider.get_config_by_name('TIPO_COMPROBANTE'))

        partner_collection_way = PartnerCollectionWay(comprobante=tipo_comprobante,
                                                      nrocomprobante=nro_tipo_comprobante,
                                                      codigocliente=str(partner.id).decode('utf-8'),
                                                      codigovalor=tipo_comprobante,
                                                      monto_cobro=total_amount,
                                                      total_cobro=total_amount,
                                                      ccosto=payment_provider.get_config_by_name('CCOSTO'),
                                                      # idcobro=collection.id,
                                                      cliente=str(partner.id).decode('utf-8'),
                                                      caja=payment_provider.get_config_by_name('CAJA'),
                                                      monto_recibido=total_amount,
                                                      collection_transaction_id=collection_trx.id
                                                      )

        collection = PartnerCollection(
            cliente=partner.id,
            monto=total_amount,
            descripcion='Pago ' + payment_provider.description,
            nro_recibo=collection_trx.payment_provider_voucher,
            comprobante=tipo_comprobante,
            cobrado=True,
            cod_cobro=PartnerCollection._next_cod_cobro(partner),
            nro_tipo_comprobante=nro_tipo_comprobante,
            details=collection_detail_list,
            collection_ways=[partner_collection_way]

        ).create()

        return collection


class PartnerCollectionDetail(db.Model):
    __tablename__ = "cobros_det"

    # id = db.Column('idcobro_det', db.Integer, autoincrement=True, primary_key=False)
    id_cobro = db.Column('id_cobro',
                         db.Integer,
                         db.ForeignKey('Cobros.Idcobro'),
                         primary_key=True,
                         autoincrement=False)
    id_cuota = db.Column('id_cuota',
                         db.Integer,
                         primary_key=True,
                         autoincrement=False)
    monto = db.Column('monto', db.Float, nullable=False)
    id_venta = db.Column('idventa', db.Integer, nullable=False, default=0)  # idlibro venta de CuotasClientes
    interes_mora = db.Column('interes_mora', db.Float, default=0)
    monto_monefactura = db.Column('monto_monefactura', db.Float, nullable=False)  # igual al monto

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PartnerCollectionWay(db.Model):
    __tablename__ = "FormaCobros"
    __table_args__ = {'implicit_returning': False}

    id = db.Column('id_formacobro', db.Integer, primary_key=True, autoincrement=True)
    comprobante = db.Column('comprobante', db.String(6), nullable=False)
    nrocomprobante = db.Column('nrocomprobante', db.Integer, nullable=False)
    codigocliente = db.Column('codigocliente', db.String(50))
    fecha_emision = db.Column('fecha_emision', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    fecha_cobro = db.Column('fecha_cobro', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    codigovalor = db.Column('codigovalor', db.String(4), nullable=False)
    moneda_cobro = db.Column('moneda_cobro', db.Integer, nullable=False, default=1)
    monto_cobro = db.Column('monto_cobro', db.Float, nullable=False)
    cotizacion = db.Column('cotizacion', db.Float, nullable=False, default=1)
    monedatotal_cobro = db.Column('monedatotal_cobro', db.Integer, nullable=False, default=1)
    total_cobro = db.Column('total_cobro', db.Float, nullable=False)
    cheque_banco = db.Column('cheque_banco', db.String(50), nullable=False, default=u'')
    cheque_nro = db.Column('cheque_nro', db.String(50), nullable=False, default=u'')
    titular_cheque = db.Column('titular_cheque', db.String(50), nullable=False, default=u'')
    nombre_codeudor = db.Column('nombre_codeudor', db.String(100), nullable=False, default=u'')
    ruc_codeudor = db.Column('ruc_codeudor', db.String(20), nullable=False, default=u'')
    nro_tarjeta = db.Column('nro_tarjeta', db.String(50), nullable=False, default=u'')
    nro_cuenta = db.Column('nro_cuenta', db.String(50), nullable=False, default=u'')
    beneficiario = db.Column('beneficiario', db.String(50), nullable=False, default=u'')
    emisor_tarjeta = db.Column('emisor_tarjeta', db.String(50), nullable=False, default=u'')
    tipo_tarjeta = db.Column('tipo_tarjeta', db.String(50), nullable=False, default=u'')
    autorizacion = db.Column('autorizacion', db.String(50), nullable=False, default=u'')
    fecha_hora_insercion = db.Column('FechaHoraInsercion', db.DateTime, default=db.func.now())
    saldoafavor = db.Column('saldoafavor', db.Boolean, nullable=False, default=0)
    ccosto = db.Column('ccosto', db.String(50), default=u'1.00.00')
    fecha_ingreso = db.Column('fecha_ingreso', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    tipo_transferencia = db.Column('tipo_transferencia', db.String(50), nullable=False, default=u'')
    destinocomprobante = db.Column('destinocomprobante', db.String(6))
    destinonrocomprobante =db.Column('destinonrocomprobante', db.Integer)
    id_ctacte = db.Column('idCtacte', db.Integer, nullable=False, default=0)
    id_cod_movi = db.Column('idCodMovi', db.Integer, nullable=False, default=0)
    id_moviclie = db.Column('id_moviclie', db.Integer)
    id_timbrado = db.Column('id_timbrado', db.Integer)
    nrofiscal = db.Column('nrofiscal', db.String(20))
    idretencion = db.Column('idretencion', db.Integer, nullable=False, default=0)
    interes_mora = db.Column('interes_mora', db.Float, default=0)
    idnotacredito_saldoafavor = db.Column('idnotacredito_saldoafavor', db.Integer, nullable=False, default=0)
    codigo = db.Column('codigo', db.Integer, nullable=False, default=0)
    idcobro = db.Column('idcobro', db.Integer, db.ForeignKey('Cobros.Idcobro'), nullable=False)
    idnotacredito = db.Column('idnotacredito', db.Integer, nullable=False, default=0)
    nrodetalle = db.Column('nrodetalle', db.Integer, nullable=False, default=1)
    documento = db.Column('documento', db.String(50), nullable=False, default=u'OPERACION EN LINEA')
    cliente = db.Column('cliente', db.Integer, nullable=False)
    pagare_cuotas = db.Column('pagare_cuotas', db.Integer, nullable=False, default=0)
    caja = db.Column('caja', db.Integer, nullable=False, default=1)  # igual que comprobante
    cajero = db.Column('cajero', db.Integer, nullable=False, default=0)
    monto_recibido = db.Column('monto_recibido', db.Float, nullable=False, default=0)
    monto_devuelto = db.Column('monto_devuelto', db.Float, nullable=False, default=0)
    desdearchivo = db.Column('desdearchivo', db.Integer, nullable=False, default=0)
    mont_real_cheq = db.Column('mont_real_cheq', db.Float, nullable=False, default=0)
    collection_transaction_id = db.Column('collection_transaction_id', db.Integer)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


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
    # access_token = fields.String()


# Debt
class PartnerDebt(db.Model):
    __tablename__ = "CuotasClientes"

    id = db.Column('Idcuota', db.Integer, primary_key=True, autoincrement=True)
    id_libroventa = db.Column('Idlibroventa', db.Integer, nullable=False)
    monto = db.Column('Monto', db.Float, nullable=False)
    estado = db.Column('Estado', db.String(50), nullable=False)
    fecha_vencimiento = db.Column('FechaVencimiento', db.Date, nullable=False)
    fecha_financiacion = db.Column('FechaFinanciacion', db.Date, nullable=False)
    nro_cuota = db.Column('NroCuota', db.Integer, nullable=False)
    saldo = db.Column('Saldo', db.Float, nullable=False)
    id_cliente = db.Column('IdCliente', db.Integer, nullable=False)
    cod_deuda_cliente = db.Column('coddeudacliente', db.Integer, nullable=False)
    pagare = db.Column('pagare', db.Boolean, nullable=False)

    def __init__(self, id_libroventa, monto, estado, fecha_vencimiento, fecha_financiacion, nro_cuota, saldo,
                 id_cliente, cod_deuda_cliente, pagare):
        self.id_libroventa = id_libroventa
        self.monto = monto
        self.estado = estado
        self.fecha_vencimiento = fecha_vencimiento
        self.fecha_financiacion = fecha_financiacion
        self.nro_cuota = nro_cuota
        self.saldo = saldo
        self.id_cliente = id_cliente
        self.cod_deuda_cliente = cod_deuda_cliente
        self.pagare = pagare

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PartnerDebtSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = PartnerDebt
        sqla_session = db.session

    amount = fields.Integer()
