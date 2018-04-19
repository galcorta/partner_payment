# -*- coding: utf-8 -*-
from ..models.factusys import VentasDet, PartnerDebt, VentasCab, Partner, CategoriasEntidadesSchema, \
    Articulo, CategoriasEntidades, Ciudad, Departamento, db, CiudadSchema, DepartamentoSchema
from ..utils import responses as resp
from ..utils.responses import response_with
from dateutil.relativedelta import relativedelta
import datetime
import json


class FactusysManager:

    def default_fecha_and_cuotas(self):
        today = datetime.date.today()
        current_month = today.month
        if current_month in [1, 2, 3]:
            return {'fecha': datetime.date(today.year, 1, 1), 'cuotas': 12}
        elif current_month in [4, 5, 6]:
            return {'fecha': datetime.date(today.year, 4, 1), 'cuotas': 9}
        elif current_month in [7, 8, 9]:
            return {'fecha': datetime.date(today.year, 7, 1), 'cuotas': 6}
        elif current_month in [10, 11, 12]:
            return {'fecha': datetime.date(today.year, 10, 1), 'cuotas': 3}

    def create_partner(self, data):
        existent_partner = Partner.query.filter(Partner.documento_identidad == data['cedula']).all()
        if not existent_partner:
            existent_partner = Partner.query.filter(Partner.documento_identidad ==
                                                    Partner.get_ruc_from_ci(data['cedula'])).all()
        if not existent_partner:
            categoria = CategoriasEntidades.query.get(data['categoryId'])
            art_id = categoria.articulo_id
            articulo = Articulo.query.get(art_id)
            if articulo:
                venta_det = VentasDet(
                    id_articulo=articulo.id,
                    unitario=articulo.precio1,
                    exentas=articulo.precio1,
                    descripcion='Venta de 1 ' + articulo.nombre,
                    FechaVencimientoArticulo=articulo.fecha_vencimiento,
                    totalvalor=articulo.precio1,
                    cuenta_contable=articulo.cuenta_venta
                )

                venta_cab = VentasCab(
                    Texentas=articulo.precio1,
                    Totalgeneral=articulo.precio1,
                    pedido=0,
                    details=[venta_det]
                )

                fecha_nacimiento = datetime.date(data['fechaNacimiento']['year'],
                                                 data['fechaNacimiento']['month'],
                                                 data['fechaNacimiento']['day'])

                partner = Partner(
                    nombre=data['fullName'].upper(),
                    razonsocial=data['fullName'].upper(),
                    documento_identidad=data['cedula'],
                    telefono=data['telefono'] if data.get('telefono') else None,
                    movil=data['celular'],
                    direccion=data['direccion'],
                    mail1=data['email'],
                    idcategoriasentidades=data['categoryId'],
                    fechanacimiento=fecha_nacimiento,
                    codciudad=data['ciudadId'],
                    coddpto_prov=data['departamentoId'],
                    proponente=data['proponente'] if data.get('proponente') else None,
                    estadocliente='PEND',
                    origen='PORTAL_WEB',
                )

                db.session.add(partner)
                db.session.flush()

                fecha_and_cuotas = self.default_fecha_and_cuotas()
                partner_debts = []
                one_mon_rel = relativedelta(months=1)
                two_mon_rel = relativedelta(months=2)
                fecha_cuota = fecha_and_cuotas['fecha']
                monto_cuota = int((articulo.precio1 - categoria.montoinicial) / 11)
                nro_cuotas = fecha_and_cuotas['cuotas']

                if nro_cuotas in [6, 12]:
                    for cuota in range(nro_cuotas):
                        fee_amount = monto_cuota
                        if cuota == 0 and nro_cuotas == 12:
                            fee_amount = categoria.montoinicial

                        partner_debts.append(PartnerDebt(monto=fee_amount,
                                                         estado='Pendiente',
                                                         fecha_vencimiento=fecha_cuota,
                                                         fecha_financiacion=datetime.datetime.today(),
                                                         nro_cuota=cuota + 1,
                                                         saldo=fee_amount,
                                                         id_cliente=partner.id))
                        fecha_cuota = fecha_cuota + one_mon_rel

                elif nro_cuotas == 9:
                    for cuota in range(7):
                        partner_debts.append(PartnerDebt(monto=(monto_cuota * 3) if cuota == 0 else monto_cuota,
                                                         estado='Pendiente',
                                                         fecha_vencimiento=fecha_cuota,
                                                         fecha_financiacion=datetime.datetime.today(),
                                                         nro_cuota=cuota + 1,
                                                         saldo=(monto_cuota * 3) if cuota == 0 else monto_cuota,
                                                         id_cliente=partner.id))
                        if cuota == 0:
                            fecha_cuota = fecha_cuota + two_mon_rel
                        fecha_cuota = fecha_cuota + one_mon_rel

                elif nro_cuotas == 3:
                    partner_debts.append(PartnerDebt(monto=monto_cuota * 3,
                                                     estado='Pendiente',
                                                     fecha_vencimiento=fecha_cuota,
                                                     fecha_financiacion=datetime.datetime.today(),
                                                     nro_cuota=1,
                                                     saldo=monto_cuota * 3,
                                                     id_cliente=partner.id))

                venta_cab.partner_debts = partner_debts
                partner.ventas = [venta_cab]
                db.session.commit()
                return response_with(resp.SUCCESS_200)
            else:
                return response_with(resp.BAD_REQUEST_400, message="Hubo un problema con su registro, por favor "
                                                                   "intente de nuevo, en caso de que continue el "
                                                                   "error, favor comunicarse con el Club")
        else:
            return response_with(resp.EXISTING_PARTNER_422, message="Ya se encuentra registrado como socio. "
                                                                    "Nro. Doc.: %r" % str(data['cedula']))

    def get_cities(self):
        fetched = Ciudad.query.all()
        ciudad_schema = CiudadSchema(many=True, only=['codciudad', 'nombre'])
        cities, error = ciudad_schema.dump(fetched)
        return cities

    def get_departments(self):
        fetched = Departamento.query.filter_by(predeterminado=False).all()
        departamento_schema = DepartamentoSchema(many=True, only=['id_departamento', 'nombre'])
        departments, error = departamento_schema.dump(fetched)
        return departments

    def get_categories(self):
        fetched = CategoriasEntidades.query.filter(CategoriasEntidades.estado == 'ACTIVO',
                                                   CategoriasEntidades.articulo_id != None,
                                                   CategoriasEntidades.web_schema != None).all()
        result = []
        for category in fetched:
            schema = json.loads(category.web_schema)
            schema['id'] = category.id
            result.append(schema)

        return result
