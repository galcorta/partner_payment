# -*- coding: utf-8 -*-
from ..models.factusys import VentasDet, PartnerDebt, VentasCab, Partner, Articulo, CategoriasEntidades, db
from ..utils import responses as resp
from ..utils.responses import response_with
from dateutil.relativedelta import relativedelta
import datetime

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
        existent_partner = Partner.query.filter(Partner.documento_identidad == data['nro_documento']).all()
        if not existent_partner:
            existent_partner = Partner.query.filter(Partner.documento_identidad ==
                                                    Partner.get_ruc_from_ci(data['nro_documento'])).all()
        if not existent_partner:
            art_id = data['articulo_id']
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

                partner = Partner(
                    nombre=data['nombre'],
                    razonsocial=data['nombre'],
                    documento_identidad=data['nro_documento'],
                    telefono=data['telefono'],
                    movil=data['celular'],
                    direccion=data['direccion'],
                    mail1=data['email'],
                    idcategoriasentidades=data['categoria_id'],
                    fechanacimiento=data['fecha_nacimiento'],
                    # ventas=[venta_cab]
                )

                db.session.add(partner)
                db.session.flush()

                fecha_and_cuotas = self.default_fecha_and_cuotas()
                categoria = CategoriasEntidades.query.get(data['categoria_id'])
                partner_debts = []
                one_mon_rel = relativedelta(months=1)
                fecha_cuota = fecha_and_cuotas['fecha']
                monto_cuota = int((articulo.precio1 - categoria.montoinicial) / 11)
                nro_cuotas = fecha_and_cuotas['cuotas']
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

                venta_cab.partner_debts = partner_debts
                partner.ventas = [venta_cab]
                db.session.commit()
                return response_with(resp.SUCCESS_200)
            else:
                return response_with(resp.BAD_REQUEST_400, message="No existe el articulo especificado")
        else:
            return response_with(resp.EXISTING_PARTNER_422)
