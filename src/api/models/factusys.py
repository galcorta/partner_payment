# -*- coding: utf-8 -*-

import datetime
import json
import math
from ...api import app, db, bcrypt
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, Schema, pre_dump
import sqlalchemy as sa
from sqlalchemy import cast, Integer
from .payment_provider import PaymentProvider


# Entidades
class Partner(db.Model):
    __tablename__ = 'Entidades'

    def next_codigo():
        max_id = db.session.query(db.func.max(Partner.id)).scalar()
        return max_id + 1

    def next_codigoEntidad():
        max_codigoEntidad = db.session.query(db.func.max(cast(Partner.codigoEntidad, Integer))).scalar()
        return str(max_codigoEntidad + 1)

    def next_nro_socio():
        max_nro_socio = db.session.query(db.func.max(cast(Partner.nro_socio, Integer))).scalar()
        return str(max_nro_socio + 1)

    id = db.Column('codigo', db.Integer, primary_key=True, default=next_codigo)
    nombre = db.Column('nombre', db.String(100), nullable=False)
    razonsocial = db.Column('razonsocial', db.String(150), nullable=False)
    documento_identidad = db.Column('ruc', db.String(20))
    cuenta_cliente = db.Column('cuenta_cliente', db.String(50), default='1.02.02.00.003')
    cuenta_proveedor = db.Column('cuenta_proveedor', db.String(50), default='')
    cuenta_receptor = db.Column('cuenta_receptor', db.String(50), default='')
    ccosto_cliente = db.Column('ccosto_cliente', db.String(20), default='1.01')
    ccosto_proveedor = db.Column('ccosto_proveedor', db.String(20), default='')
    ccosto_receptor = db.Column('ccosto_receptor', db.String(20), default='')
    telefono = db.Column('telefono', db.String(20))
    fax = db.Column('fax', db.String(20), default='')
    movil = db.Column('movil', db.String(20))
    direccion = db.Column('direccion', db.String(200))
    localidad = db.Column('localidad', db.String(200), default='')
    estado = db.Column('estado', db.String(200), default='ACTIVO')
    pais = db.Column('pais', db.String(100), default='9')
    codpostal = db.Column('codpostal', db.String(30), default='')
    mail1 = db.Column('mail1', db.String(100), default='')
    mail2 = db.Column('mail2', db.String(100), default='')
    website = db.Column('website', db.String(200), default='')
    libre = db.Column('libre', db.String(200), default='')
    telefono_per = db.Column('telefono_per', db.String(20), default='')
    fax_per = db.Column('fax_per', db.String(20), default='')
    movil_per = db.Column('movil_per', db.String(20), default='')
    direccion_per = db.Column('direccion_per', db.String(200), default='')
    localidad_per = db.Column('localidad_per', db.String(200), default='')
    estado_per = db.Column('estado_per', db.String(200), default='')
    pais_per = db.Column('pais_per', db.String(100), default='')
    codpostal_per = db.Column('codpostal_per', db.String(30), default='')
    mail1_per = db.Column('mail1_per', db.String(100), default='')
    mail2_per = db.Column('mail2_per', db.String(100), default='')
    nota = db.Column('nota', db.String(500), default='')
    certificadoexencion = db.Column('certificadoexencion', db.SmallInteger, nullable=False, default=0)
    cliente = db.Column('cliente', db.Boolean, nullable=False, default=True)
    proveedor = db.Column('proveedor', db.Boolean, nullable=False, default=False)
    receptor = db.Column('receptor', db.Boolean, nullable=False, default=False)
    funcionario = db.Column('funcionario', db.Boolean, nullable=False, default=False)
    codigo_ant = db.Column('codigo_ant', db.Integer, default=0)
    codempresa = db.Column('codempresa', db.Integer, default=0)
    codcategoria = db.Column('codcategoria', db.Integer, nullable=False, default=0)
    estadocliente = db.Column('estadocliente', db.String(10), nullable=False, default='ACTI')
    id_zona = db.Column('id_zona', db.Integer, nullable=False, default=1)
    id_zona_per = db.Column('id_zona_per', db.Integer, nullable=False, default=0)
    idmoneda = db.Column('idmoneda', db.Integer, nullable=False, default=1)
    montosolafirma = db.Column('montosolafirma', db.Float, nullable=False, default=0)
    totallineacred = db.Column('totallineacred', db.Float, nullable=False, default=0)
    saldoactual = db.Column('saldoactual', db.Float, nullable=False, default=0)
    chequeslimitecredito = db.Column('chequeslimitecredito', db.Float, nullable=False, default=0)
    creditodisponible = db.Column('creditodisponible', db.Float, nullable=False, default=0)
    plazopagos = db.Column('plazopagos', db.String(50), nullable=False, default='')
    chequesext = db.Column('chequesext', db.Float, nullable=False, default=0)
    propiedades = db.Column('propiedades', db.Float, nullable=False, default=0)
    rodados = db.Column('rodados', db.Float, nullable=False, default=0)
    impedirfacturar = db.Column('impedirfacturar', db.Boolean, nullable=False, default=False)
    aplicardescuento = db.Column('aplicardescuento', db.Boolean, nullable=False, default=False)
    telefono2 = db.Column('telefono2', db.String(20), nullable=False, default='')
    telefono3 = db.Column('telefono3', db.String(20), nullable=False, default='')
    fax2 = db.Column('fax2', db.String(20), nullable=False, default='')
    codruta = db.Column('codruta', db.Integer, nullable=False, default=1)
    codrubroprincipal = db.Column('codrubroprincipal', db.Integer, nullable=False, default=0)
    codrubroadicional1 = db.Column('codrubroadicional1', db.Integer, nullable=False, default=0)
    codrubroadicional2 = db.Column('codrubroadicional2', db.Integer, nullable=False, default=0)
    notacliente = db.Column('notacliente', db.String(500), nullable=False, default='')
    montorodados = db.Column('montorodados', db.Float, nullable=False, default=0)
    direccion2 = db.Column('direccion2', db.String(200), nullable=False, default='')
    rucadicional = db.Column('rucadicional', db.String(20), nullable=False, default='')
    montocheques = db.Column('montocheques', db.Float, nullable=False, default=0)
    montopropiedades = db.Column('montopropiedades', db.Float, nullable=False, default=0)
    codpais = db.Column('codpais', db.Integer, default=9)
    codciudad = db.Column('codciudad', db.Integer, nullable=False, default=0)
    coddpto_prov = db.Column('coddpto_prov', db.Integer, nullable=False, default=0)
    codpais_per = db.Column('codpais_per', db.Integer, nullable=False, default=0)
    codciudad_per = db.Column('codciudad_per', db.Integer, nullable=False, default=0)
    coddpto_prov_per = db.Column('coddpto_prov_per', db.Integer, nullable=False, default=0)
    codmonedalc = db.Column('codmonedalc', db.Integer, nullable=False, default=0)
    monedacheques = db.Column('monedacheques', db.Integer, nullable=False, default=0)
    monedapropiedades = db.Column('monedapropiedades', db.Integer, nullable=False, default=0)
    monedarodados = db.Column('monedarodados', db.Integer, nullable=False, default=0)
    movil_per1 = db.Column('movil_per1', db.String(20), nullable=False, default='')
    movil_per2 = db.Column('movil_per2', db.String(20), nullable=False, default='')
    contacto = db.Column('contacto', db.Boolean, default=False)
    categoria = db.Column('categoria', db.Integer, nullable=False, default=0)
    ctacatastral = db.Column('ctacatastral', db.String(50), nullable=False, default='')
    idrubro = db.Column('idrubro', db.Integer, nullable=False, default=1)
    ctactecatastral = db.Column('ctactecatastral', db.String(50), nullable=False, default='')
    nro_medidor = db.Column('nroMedidor', db.String(20), nullable=False, default='')
    tiene_medidor = db.Column('tieneMedidor', db.Boolean, nullable=False, default=False)
    tipo_medidor = db.Column('tipoMedidor', db.String(15), nullable=False, default='')
    zona = db.Column('zona', db.String(100), nullable=False, default='')
    zona_per = db.Column('zona_per', db.String(100), nullable=False, default='')
    ruchechauka = db.Column('ruchechauka', db.String(20), nullable=False, default='44444401-7')
    comision_vendedor = db.Column('comision_vendedor', db.Float, nullable=False, default=0)
    comision_cobrador = db.Column('comision_cobrador', db.Float, nullable=False, default=0)
    usuario = db.Column('usuario', db.Integer, nullable=False, default=0)
    ubicacion = db.Column('ubicacion', db.Integer, default=0)
    idlista_cab = db.Column('idlista_cab', db.Integer, default=1)
    fecha_alta = db.Column('fechaAlta', db.DateTime, default=datetime.datetime.now)
    idvendedor = db.Column('idvendedor', db.Integer, default=3)
    condicion_pago = db.Column('CondiciondePago', db.String(10), nullable=False, default='')
    entidad_relacionada = db.Column('entidad_relacionada', db.Integer, nullable=False, default=0)
    nro_registro_distribuidor = db.Column('nroRegistro_Distribuidor', db.String(100), nullable=False, default='')
    fechavto_registro_distribuidor = db.Column('fechaVto_Registro_Distribuidor', db.Date, nullable=False,
                                               default=sa.text("CONVERT(date, GETDATE())"))
    cliente_exterior = db.Column('cliente_exterior', db.Boolean, nullable=False, default=False)
    beneficiario = db.Column('beneficiario', db.String(100), default='')
    codigo_vendedor = db.Column('codigo_vendedor', db.Integer, nullable=False, default=0)
    codigoEntidad = db.Column('codigoEntidad', db.String(50), nullable=False, default=next_codigoEntidad)
    formadepago = db.Column('formadepago', db.String(20), default='')
    contribuyente = db.Column('contribuyente', db.Boolean, nullable=False, default=False)
    personalsuperior = db.Column('personalsuperior', db.Boolean, nullable=False, default=False)
    plazoproveedor = db.Column('plazoproveedor', db.String(50), nullable=False, default='')
    condicionproveedor = db.Column('condicionproveedor', db.String(50), nullable=False, default='')
    idlocalidad = db.Column('idlocalidad', db.Integer, default=1)
    codigopais = db.Column('codigopais', db.Integer, default=9)
    dias_trabajados = db.Column('dias_trabajados', db.Integer, nullable=False, default=1)
    idcategoriasentidades = db.Column('idcategoriasentidades', db.Integer)
    idtipocomp_lote = db.Column('idtipocomp_lote', db.Integer)
    idproyecto = db.Column('idproyecto', db.Integer, nullable=False, default=0)
    descuento = db.Column('descuento', db.Float, nullable=False, default=0)
    modeloImpresion = db.Column('modeloImpresion', db.String(50), nullable=False, default='')
    interesMora = db.Column('interesMora', db.Float, nullable=False, default=0)
    recargarmontoenfactura = db.Column('recargarmontoenfactura', db.Boolean, nullable=False, default=False)
    codigo_cobrador = db.Column('codigo_cobrador', db.Integer, nullable=False, default=0)
    UserUpdate = db.Column('UserUpdate', db.Integer, default=3)
    FechaUpdate = db.Column('FechaUpdate', db.DateTime, default=datetime.datetime.now)
    UserInsert = db.Column('UserInsert', db.Integer, default=3)
    FechaInsert = db.Column('FechaInsert', db.DateTime, default=datetime.datetime.now)
    situaciontesaka = db.Column('situaciontesaka', db.String(50), default='CONTRIBUYENTE')
    tipoidentificacion = db.Column('tipoidentificacion', db.String(50), default='NINGUNO')
    identificacion = db.Column('identificacion', db.String(50), default='')
    conceptoReteIva = db.Column('conceptoReteIva', db.Integer, default=4)
    conceptoReteRenta = db.Column('conceptoReteRenta', db.Integer, default=8)
    nro_socio = db.Column('nrosocio', db.String(50), nullable=False, default=next_nro_socio)
    fechanacimiento = db.Column('fechanacimiento', db.Date)
    proponente = db.Column('proponente', db.String(150))
    origen = db.Column('origen', db.String(15))

    ventas = db.relationship('VentasCab', backref='partner', lazy='dynamic')

    def verify_password(self, password):
        first3_name = self.nombre.lower().strip()[:3]
        last3_ci = self.documento_identidad.strip()[-3:]
        correct_password = first3_name + last3_ci
        return password.lower() == correct_password

    @staticmethod
    def get_ruc_from_ci(vat):
        for c in str(vat):
            if not c.isdigit():
                return vat
        basemax = 11
        k = 2
        total = 0
        for c in reversed(vat):
            n = int(c)
            if n > basemax:
                k = 2
            total += n * k
            k += 1
        resto = total % basemax
        if resto > 1:
            n = basemax - resto
        else:
            n = 0
        return vat + '-' + str(n)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Partner %r>' % self.nombre


# Cobros
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
    cobrado = db.Column('cobrado', db.Boolean, nullable=False, default=True)
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

    def create(self, debts, collection_trx):
        partner = Partner.query.get(debts[0].id_cliente)
        payment_provider = collection_trx.payment_provider
        tipo_comprobante = payment_provider.get_config_by_name('TIPO_COMPROBANTE')
        nro_tipo_comprobante = PartnerCollection._next_nrotipocomprobante(partner, tipo_comprobante)
        ccosto = payment_provider.get_config_by_name('CCOSTO')
        caja = payment_provider.get_config_by_name('CAJA')
        cobrador = payment_provider.get_config_by_name('COBRADOR')

        total_amount = 0
        for debt in debts:
            total_amount += debt.amount
            self.details.append(PartnerCollectionDetail(id_cuota=debt.id,
                                                        monto=debt.amount,
                                                        id_venta=debt.id_libroventa,
                                                        monto_monefactura=debt.amount))
            debt.saldo -= debt.amount
            debt.estado = 'Cobrado'

        self.collection_ways.append(PartnerCollectionWay(comprobante=tipo_comprobante,
                                                         nrocomprobante=nro_tipo_comprobante,
                                                         codigocliente=str(partner.id).decode('utf-8'),
                                                         codigovalor=tipo_comprobante,
                                                         monto_cobro=total_amount,
                                                         total_cobro=total_amount,
                                                         ccosto=ccosto,
                                                         cliente=str(partner.id).decode('utf-8'),
                                                         caja=caja,
                                                         monto_recibido=total_amount,
                                                         collection_transaction_id=collection_trx.id
                                                         ))

        self.cliente = partner.id
        self.monto = total_amount
        self.descripcion = 'Pago ' + payment_provider.description
        self.nro_recibo = collection_trx.payment_provider_voucher
        self.cobrador = cobrador
        self.comprobante = tipo_comprobante
        self.cod_cobro = PartnerCollection._next_cod_cobro(partner)
        self.nro_tipo_comprobante = nro_tipo_comprobante

        if partner.origen == 'PORTAL_WEB' and partner.estadocliente == 'PEND':
            partner.estadocliente = 'ACTI'
            db.session.add(partner)

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
    def get_by_collection(collection):
        return PartnerCollection.query \
            .filter(PartnerCollection.collection_ways
                    .any(PartnerCollectionWay.collection_transaction_id == collection.id)).one_or_none()

    def cancel_collection(self):
        for det in self.details:
            partner_debt = PartnerDebt.query.get(det.id_cuota)
            partner_debt.saldo += det.monto
            partner_debt.estado = 'Pendiente'

        self.estado = 'ANULADO'
        db.session.add(self)
        db.session.commit()
        return True


# cobros_det
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


# FormaCobro
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


class MigPagosElectronicos(db.Model):
    __tablename__ = 'MigPagosElectronicos'

    id = db.Column('id', db.Integer, primary_key=True)
    nro_socio = db.Column('nro_socio', db.Integer)
    nro_documento = db.Column('nro_documento', db.String(50))
    monto = db.Column('monto', db.Integer)
    anho = db.Column('anho', db.Integer)
    nro_cuota = db.Column('nro_cuota', db.Integer)
    fecha_pago = db.Column('fecha_pago', db.Date)
    migrado = db.Column('migrado', db.Boolean)
    descripcion = db.Column('descripcion', db.String(255))

    # @staticmethod
    # def run_migration():
    #     payment_provider = PaymentProvider.query.filter(PaymentProvider.name == 'aquipago').one()
    #     tipo_comprobante = payment_provider.get_config_by_name('TIPO_COMPROBANTE')
    #     ccosto = payment_provider.get_config_by_name('CCOSTO')
    #     caja = payment_provider.get_config_by_name('CAJA')
    #     cobrador = payment_provider.get_config_by_name('COBRADOR')
    #
    #     pagos_electronicos = MigPagosElectronicos.query.all()
    #     for pago in pagos_electronicos:
    #         partners = Partner.query.filter(Partner.documento_identidad.contains(pago.nro_documento)).all()
    #         if partners:
    #             partner, debts = None, None
    #             for item in partners:
    #                 debts = PartnerDebt.query.filter(PartnerDebt.id_cliente == item.id,
    #                                                  PartnerDebt.estado == 'Pendiente',
    #                                                  PartnerDebt.saldo > 0).all()
    #                 if debts:
    #                     partner = item
    #                     break
    #
    #             if partner:
    #                 nro_tipo_comprobante = PartnerCollection._next_nrotipocomprobante(partner, tipo_comprobante)
    #                 collection = PartnerCollection()
    #                 collection.collection_ways.append(PartnerCollectionWay(comprobante=tipo_comprobante,
    #                                                                        nrocomprobante=nro_tipo_comprobante,
    #                                                                        codigocliente=str(partner.id).decode(
    #                                                                            'utf-8'),
    #                                                                        codigovalor=tipo_comprobante,
    #                                                                        monto_cobro=pago.monto,
    #                                                                        total_cobro=pago.monto,
    #                                                                        ccosto=ccosto,
    #                                                                        cliente=str(partner.id).decode('utf-8'),
    #                                                                        caja=caja,
    #                                                                        monto_recibido=pago.monto,
    #                                                                        fecha_cobro=pago.fecha_pago,
    #                                                                        fecha_emision=pago.fecha_pago
    #                                                                        ))
    #                 amount = pago.monto
    #                 for debt in debts:
    #                     if amount > debt.saldo:
    #                         monto_pago = debt.saldo
    #                         amount -= debt.saldo
    #                         debt.saldo = 0
    #                     else:
    #                         monto_pago = amount
    #                         debt.saldo -= amount
    #                         amount = 0
    #
    #                     if debt.saldo == 0:
    #                         debt.estado = 'Cobrado'
    #
    #                     collection.details.append(PartnerCollectionDetail(id_cuota=debt.id,
    #                                                                       monto=monto_pago,
    #                                                                       id_venta=debt.id_libroventa,
    #                                                                       monto_monefactura=monto_pago))
    #                     if amount == 0:
    #                         break
    #
    #                 collection.cliente = partner.id
    #                 collection.fecha_cobro = pago.fecha_pago
    #                 collection.monto = (pago.monto - amount)
    #                 collection.descripcion = 'Pago ' + payment_provider.description + '(Migrado)'
    #                 collection.nro_recibo = str(pago.nro_socio) + '-' + str(pago.nro_cuota)
    #                 collection.cobrador = cobrador
    #                 collection.comprobante = tipo_comprobante
    #                 collection.cod_cobro = PartnerCollection._next_cod_cobro(partner)
    #                 collection.nro_tipo_comprobante = nro_tipo_comprobante
    #
    #                 if amount:
    #                     pago.descripcion = "Dinero sobrante: " + str(amount)
    #                     print "Nro Documento: " + partner.documento_identidad + " - Sobrante: " + str(amount)
    #
    #                 pago.migrado = True
    #                 db.session.add(collection)
    #                 db.session.add(pago)
    #                 db.session.commit()
    #                 print "Pago Nro: " + str(pago.id)
    #
    #             else:
    #                 pago.migrado = False
    #                 pago.descripcion = "No se encuentran deudas pendientes del Socio"
    #                 db.session.add(pago)
    #                 db.session.commit()
    #                 print "Nro Documento2: " + pago.nro_documento + " - Sobrante: " + str(pago.monto)
    #         else:
    #             pago.migrado = False
    #             pago.descripcion = "No se encuentra el Socio"
    #             db.session.add(pago)
    #             db.session.commit()
    #             print "No se encuentra el Socio - Nro Documento: " + pago.nro_documento

    def __repr__(self):
        return '<Partner {0}>'.format(self.nombre)


# CuotasClientes
class PartnerDebt(db.Model):
    __tablename__ = "CuotasClientes"

    id = db.Column('Idcuota', db.Integer, primary_key=True, autoincrement=True)
    id_libroventa = db.Column('Idlibroventa',
                              db.Integer,
                              db.ForeignKey('Ventas_cab.codigo'),
                              nullable=False)
    monto = db.Column('Monto', db.Float, nullable=False)
    estado = db.Column('Estado', db.String(50), nullable=False)
    fecha_vencimiento = db.Column('FechaVencimiento', db.Date, nullable=False)
    fecha_financiacion = db.Column('FechaFinanciacion', db.Date, nullable=False)
    nro_cuota = db.Column('NroCuota', db.Integer, nullable=False)
    saldo = db.Column('Saldo', db.Float, nullable=False)
    id_cliente = db.Column('IdCliente', db.Integer, nullable=False)
    cod_deuda_cliente = db.Column('coddeudacliente', db.Integer, nullable=False, default=0)
    pagare = db.Column('pagare', db.Boolean, nullable=False, default=0)

    # def __init__(self, id_libroventa, monto, estado, fecha_vencimiento, fecha_financiacion, nro_cuota, saldo,
    #              id_cliente, cod_deuda_cliente, pagare):
    #     self.id_libroventa = id_libroventa
    #     self.monto = monto
    #     self.estado = estado
    #     self.fecha_vencimiento = fecha_vencimiento
    #     self.fecha_financiacion = fecha_financiacion
    #     self.nro_cuota = nro_cuota
    #     self.saldo = saldo
    #     self.id_cliente = id_cliente
    #     self.cod_deuda_cliente = cod_deuda_cliente
    #     self.pagare = pagare

    def __repr__(self):
        return '<PartnerDebt %r>' % str(self.id)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


# Ventas_Cab
class VentasCab(db.Model):
    __tablename__ = "Ventas_cab"

    def next_nrocomprobante():
        max_nrocomprobante = db.session.query(db.func.max(VentasCab.nrocomprobante)).scalar()
        return max_nrocomprobante + 1

    def next_codigo():
        max_id = db.session.query(db.func.max(VentasCab.id)).scalar()
        return max_id + 1

    def next_nroboleta():
        last_venta_cab = VentasCab.query.filter(VentasCab.tipocomprobante == 'VA').order_by(VentasCab.id.desc()).first()
        last_nroboleta = last_venta_cab.nroboleta
        next_nro = int(last_nroboleta.split('-')[2]) + 1
        return last_nroboleta.split('-')[0] + '-' + last_nroboleta.split('-')[1] + '-' + str(next_nro).zfill(7)

    def default_cuotas():
        current_month = datetime.date.today().month
        if current_month in [1, 2, 3]:
            return 12
        elif current_month in [4, 5, 6]:
            return 9
        elif current_month in [7, 8, 9]:
            return 6
        elif current_month in [10, 11, 12]:
            return 3

    def default_fecha_cuota():
        today = datetime.date.today()
        current_month = today.month
        if current_month in [1, 2, 3]:
            return datetime.date(today.year, 1, 1)
        elif current_month in [4, 5, 6]:
            return datetime.date(today.year, 4, 1)
        elif current_month in [7, 8, 9]:
            return datetime.date(today.year, 7, 1)
        elif current_month in [10, 11, 12]:
            return datetime.date(today.year, 10, 1)

    def next_nrocontrol():
        max_NroControl = db.session.query(db.func.max(VentasCab.NroControl))\
            .filter(VentasCab.tipocomprobante == 'VA').scalar()
        return max_NroControl + 1

    def default_hora_inicio_fin():
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    id = db.Column('codigo', db.Integer, primary_key=True, default=next_codigo)
    nrocomprobante = db.Column('nrocomprobante', db.Integer, nullable=False, default=next_nrocomprobante)
    tipocomprobante = db.Column('tipocomprobante', db.String(6), nullable=False, default='VA')
    fecha = db.Column('fecha', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    fechacarga = db.Column('fechacarga', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    Texentas = db.Column('Texentas', db.Float, nullable=False)
    Tgravadas = db.Column('Tgravadas', db.Float, nullable=False, default=0)
    Tdescuento = db.Column('Tdescuento', db.Float, nullable=False, default=0)
    Tiva = db.Column('Tiva', db.Float, nullable=False, default=0)
    Totalgeneral = db.Column('Totalgeneral', db.Float, nullable=False)
    descuento = db.Column('descuento', db.Float, nullable=False, default=0)
    agente = db.Column('agente', db.Integer, nullable=False, default=1)
    cliente = db.Column('cliente',
                        db.Integer,
                        db.ForeignKey('Entidades.codigo'),
                        nullable=False)
    formapago = db.Column('formapago', db.Integer, nullable=False, default=1)
    lista = db.Column('lista', db.Integer, nullable=False, default=1)
    nroboleta = db.Column('nroboleta', db.String(15), nullable=False, default=next_nroboleta)
    timbrado = db.Column('timbrado', db.Integer, nullable=False, default=1)
    moneda = db.Column('moneda', db.Integer, nullable=False, default=1)
    cotizacion = db.Column('cotizacion', db.Float, nullable=False, default=1)
    remision = db.Column('remision', db.String(15), nullable=False, default=0)
    cuotas = db.Column('cuotas', db.Integer, nullable=False, default=default_cuotas)
    comision = db.Column('comision', db.Float, nullable=False, default=0)
    fechacuota = db.Column('fechacuota', db.Date, nullable=False, default=default_fecha_cuota)
    plazocuota = db.Column('plazocuota', db.Integer, nullable=False, default=30)
    docupago = db.Column('docupago', db.Integer, nullable=False, default=0)
    sucursal = db.Column('sucursal', db.Integer, nullable=False, default=1)
    tipoemision = db.Column('tipoemision', db.SmallInteger, nullable=False, default=1)
    NroControl = db.Column('NroControl', db.Integer, nullable=False, default=next_nrocontrol)
    idzona = db.Column('idzona', db.Integer, nullable=False, default=1)
    estado = db.Column('estado', db.String(50), nullable=False, default='ACTIVO')
    cobrador = db.Column('cobrador', db.Integer, nullable=False, default=40)
    comision_cobrador = db.Column('comision_cobrador', db.Float, nullable=False, default=0)
    pedido = db.Column('pedido', db.Integer, nullable=False)
    sucursal_cliente = db.Column('sucursal_cliente', db.Integer, nullable=False, default=0)
    impreso = db.Column('impreso', db.Boolean, nullable=False, default=0)
    id_proyecto = db.Column('id_proyecto', db.Integer, nullable=False, default=1)
    idusuario = db.Column('idusuario', db.Integer, default=3)
    nro_mesa = db.Column('nro_mesa', db.Integer, nullable=False, default=0)
    cantidad_cubiertos = db.Column('cantidad_cubiertos', db.Integer, nullable=False, default=0)
    cod_mozo = db.Column('cod_mozo', db.Integer, nullable=False, default=0)
    nota = db.Column('nota', db.String(8000), nullable=False, default='')
    ccosto = db.Column('ccosto', db.String(50), default='1.00')
    idplan = db.Column('idplan', db.Integer)
    comisionfija = db.Column('comisionfija', db.Float, nullable=False, default=0)
    deposito = db.Column('deposito', db.Integer, default=1)
    afectar_a = db.Column('afectar_a', db.Integer, nullable=False, default=0)
    nro_habitacion = db.Column('nro_habitacion', db.String(50), nullable=False, default=0)
    hora_inicio = db.Column('hora_inicio', db.String(50), nullable=False, default=default_hora_inicio_fin)
    hora_fin = db.Column('hora_fin', db.String(50), nullable=False, default=default_hora_inicio_fin)
    fechaingreso = db.Column('fechaingreso', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    nro_registro = db.Column('nro_registro', db.String(200), nullable=False, default='')
    fecha_hora_creacion = db.Column('fecha_hora_creacion', db.DateTime, nullable=False, default=datetime.datetime.now)
    fecha_hora_ultimamodificacion = db.Column('fecha_hora_ultimamodificacion', db.DateTime, nullable=False,
                                              default=datetime.datetime.now)
    cod_control = db.Column('cod_control', db.String(200), nullable=False, default='')
    idtimbrado = db.Column('idtimbrado', db.Integer, default=1)
    contadorimpresion = db.Column('contadorimpresion', db.Integer, nullable=False, default=0)
    ciclo = db.Column('ciclo', db.String(50), nullable=False, default='')
    comprobante_origen = db.Column('comprobante_origen', db.String(50), nullable=False, default='')
    nrocomprobante_origen = db.Column('nrocomprobante_origen', db.Integer, nullable=False, default=0)
    tabla_sistema = db.Column('tabla_sistema', db.Integer, nullable=False, default=0)
    UserUpdate = db.Column('UserUpdate', db.Integer)
    FechaUpdate = db.Column('FechaUpdate', db.DateTime)
    UserInsert = db.Column('UserInsert', db.Integer, default=3)
    FechaInsert = db.Column('FechaInsert', db.DateTime, default=datetime.datetime.now)
    chofer = db.Column('chofer', db.Integer, nullable=False, default=0)
    NroChapa = db.Column('NroChapa', db.String(50), nullable=False, default='')
    kilometro = db.Column('kilometro', db.String(50), nullable=False, default='')
    camion = db.Column('camion', db.Integer, nullable=False, default=0)
    color = db.Column('color', db.String(50), nullable=False, default='')
    comprobante_relacionado = db.Column('comprobante_relacionado', db.String(50), nullable=False, default='')
    nrocomprobante_relacionado = db.Column('nrocomprobante_relacionado', db.Integer, nullable=False, default=0)

    details = db.relationship('VentasDet', backref='venta', lazy='dynamic')
    partner_debts = db.relationship('PartnerDebt', backref='venta', lazy='dynamic')

    def __repr__(self):
        return '<VentasCab %r>' % self.nroboleta

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


# Ventas_det
class VentasDet(db.Model):
    __tablename__ = "Ventas_det"

    codigo = db.Column('codigo',
                       db.Integer,
                       db.ForeignKey('Ventas_cab.codigo'),
                       primary_key=True)
    item = db.Column('item', db.Integer, primary_key=True, default=1)
    id_articulo = db.Column('id_articulo', db.Integer)
    articulo = db.Column('articulo', db.String(50), nullable=False, default='')
    serie = db.Column('serie', db.String(10), nullable=False, default=1)
    cantidad = db.Column('cantidad', db.Float, nullable=False, default=1)
    unitario = db.Column('unitario', db.Float, nullable=False)
    exentas = db.Column('exentas', db.Float, nullable=False)
    gravadas = db.Column('gravadas', db.Float, nullable=False, default=0)
    iva = db.Column('iva', db.Float, nullable=False, default=0)
    porcentaje = db.Column('porcentaje', db.Float, nullable=False, default=0)
    incluido = db.Column('incluido', db.String, nullable=False, default='N')
    desc_porc = db.Column('desc_porc', db.Float, nullable=False, default=0)
    descuento = db.Column('descuento', db.Float, nullable=False, default=0)
    descripcion = db.Column('descripcion', db.String(50), nullable=False)
    ccosto = db.Column('ccosto', db.String(20), nullable=False, default='1.00')
    deposito = db.Column('deposito', db.Integer, nullable=False, default=1)
    fecha = db.Column('fecha', db.Date, nullable=False, default=sa.text("CONVERT(date, GETDATE())"))
    moneda = db.Column('moneda', db.Integer, nullable=False, default=1)
    lista = db.Column('lista', db.Integer, default=1)
    cotizacion = db.Column('cotizacion', db.Float, nullable=False, default=1)
    nroserie = db.Column('nroserie', db.String(50), nullable=False, default='')
    unitariooriginal = db.Column('unitariooriginal', db.Float, nullable=False, default=0)
    idlista_det = db.Column('idlista_det', db.Integer)
    FechaVencimientoArticulo = db.Column('FechaVencimientoArticulo', db.Date)
    lote = db.Column('lote', db.String(50), nullable=False, default='')
    comision_articulo = db.Column('comision_articulo', db.Float, nullable=False, default=0)
    detalle_tipeado = db.Column('detalle_tipeado', db.String(800), nullable=False, default='')
    presentacion_embalaje = db.Column('presentacion_embalaje', db.Float, nullable=False, default=1)
    id_embalajesalida = db.Column('id_embalajesalida', db.Integer, default=1)
    totalvalor = db.Column('totalvalor', db.Float, nullable=False)
    porcentaje_gravado = db.Column('porcentaje_gravado', db.Float, nullable=False, default=0)
    impuestoadicional = db.Column('impuestoadicional', db.Float, nullable=False, default=0)
    cuenta_contable = db.Column('cuenta_contable', db.String(50), nullable=False)
    imprimir_item = db.Column('imprimir_item', db.Boolean, nullable=False, default=1)
    formulario = db.Column('formulario', db.String(20), default='')
    codigoimpuesto = db.Column('codigoimpuesto', db.Integer, default=0)
    formulario_ref = db.Column('formulario_ref', db.String(20), default='')

    def __repr__(self):
        return '<VentasDet %r>' % self.descripcion


class Ciudad(db.Model):
    __tablename__ = "Ciudades"

    codciudad = db.Column('codciudad', db.Integer, primary_key=True)
    idciudad = db.Column('idciudad', db.Integer, autoincrement=True, nullable=False)
    nombre = db.Column('nombre', db.String(50), nullable=False)
    codpais = db.Column('codpais', db.Integer, nullable=False)


class Departamento(db.Model):
    __tablename__ = "Departamentos"

    id_departamento = db.Column('id_departamento', db.Integer, primary_key=True, autoincrement=True)
    codcontrol = db.Column('codcontrol', db.String(50), nullable=False)
    nombre = db.Column('nombre', db.String(200), nullable=False)
    descripcion = db.Column('descripcion', db.String(500), nullable=False)
    predeterminado = db.Column('predeterminado', db.Boolean, nullable=False)


class Pais(db.Model):
    __tablename__ = "Paises"

    codpais = db.Column('codpais', db.Integer, primary_key=True)
    idpais = db.Column('idpais', db.Integer, autoincrement=True, nullable=False)
    nombre = db.Column('nombre', db.String(50), nullable=False)
    abreviatura = db.Column('abreviatura', db.String(4), nullable=False)
    descripcion = db.Column('descripcion', db.String(100))
    predeterminado = db.Column('predeterminado', db.Boolean, nullable=False)


# Articulo
class Articulo(db.Model):
    __tablename__ = "Articulos"

    id = db.Column('id_articulo', db.Integer, primary_key=True)
    nombre = db.Column('nombre', db.String(500), nullable=False)
    precio1 = db.Column('precio1', db.Float, nullable=False)
    fecha_vencimiento = db.Column('fecha_vencimiento', db.Date)
    cuenta_venta = db.Column('cuenta_venta', db.String(50))

    def __repr__(self):
        return '<Articulo %r>' % self.nombre


# CategoriasEntidades
class CategoriasEntidades(db.Model):
    __tablename__ = "CategoriasEntidades"

    id = db.Column('idcategoriasentidades', db.Integer, primary_key=True, autoincrement=True)
    codcontrol = db.Column('codcontrol', db.String(50), nullable=False)
    nombre = db.Column('nombre', db.String(200), nullable=False)
    descripcion = db.Column('descripcion', db.String(200), nullable=False)
    montocategoria = db.Column('montocategoria', db.Float, nullable=False)
    montoinicial = db.Column('montoinicial', db.Float, nullable=False)
    vigenciadesde = db.Column('vigenciadesde', db.Date, nullable=False)
    vigenciahasta = db.Column('vigenciahasta', db.Date, nullable=False)
    estado = db.Column('estado', db.String(15), nullable=False)
    articulo_id = db.Column('articulo_id', db.Integer)
    web_schema = db.Column('web_schema', db.Text)


# Model Schemas
class PartnerDebtSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = PartnerDebt
        sqla_session = db.session

    amount = fields.Integer()
    pending = fields.Boolean()


class PartnerSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Partner
        sqla_session = db.session


class CiudadSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Ciudad
        sqla_session = db.session


class DepartamentoSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Departamento
        sqla_session = db.session


class CategoriasEntidadesSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = CategoriasEntidades
        sqla_session = db.session


# Schemas
class PartnerLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class PartnerLoginResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    username = fields.String()
    state = fields.String()
    nro_socio = fields.String()


