from odoo import http, models, fields, api, _
from datetime import datetime, timedelta
import calendar
from odoo.exceptions import RedirectWarning, UserError
import requests, json
import base64
from odoo.tools.safe_eval import safe_eval
import json

import logging
_logger = logging.getLogger(__name__)


class ResCountry(models.Model):
    _inherit = 'res.country'

    sap_code = fields.Char(size=20,string="SAP Code")

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    sap_code = fields.Char(size=20,string="SAP Code")

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    sap_code = fields.Char(size=20,string="SAP Code")

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    sap_code = fields.Char(size=20,string="SAP Code")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sap_code = fields.Char(size=20,string="SAP Code")
    dist_channel = fields.Integer(string="Distribution Cannel",translate=True)
    sap_material_id = fields.Many2one('sap.material',string="SAP Material", translate=True)
    KONV_WAERS = fields.Many2one('sap.waers', string="KONV_WAERS",translate=True)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sap_code = fields.Char(size=20,string="SAP Code")

class UomUom(models.Model):
    _inherit = 'uom.uom'

    sap_code = fields.Char(size=20,string="SAP Code")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vbak_vkorg_id = fields.Many2one('sap.vbak.vkorg',string="Sales Organizacion")
    vbak_vtweg_id = fields.Many2one('sap.vbak.vtweg',string="Distribution Channel")
    vbak_spart_id = fields.Many2one('sap.vbak.spart',string="Sector")
    vbuk_cmpsb = fields.Char(size=50,string="Credit Block (limit)")
    vbuk_cmpsf = fields.Char(size=50,string="Credit Block (due)")
    vbuk_cmpsg = fields.Char(size=50,string="Credit Block (old)")
    vbuk_cmgst = fields.Char(size=50,string="Credit Block (global)")
    ec_dest_id = fields.Many2one('res.partner',string="Economic Destiny")
    pickup = fields.Boolean(string="Pickup",translate=True)
    vbap_werks = fields.Many2one('sap.werk',string="Delivering Plant")
    sap_document_type_id = fields.Many2one('sap.vbak.auart',string="SAP Document Type",translate=True)
    start_date = fields.Date(string="Start Date",translate=True)
    sap_code = fields.Char(size=20,string="SAP Code Order",translate=True,index=True)
    note_obs = fields.Text(string="Observaciones",help="Observaciones",translate=True)
    note_inv = fields.Text(string="Invoice Notes",help="Invoice Notes",translate=True)
    sap_result = fields.Char(size=6,string="Result")
    sap_message_recieved = fields.Text(string="Message Received")
    sap_message_sent = fields.Text(string="Message Sent")
    state = fields.Selection(selection_add=[('sent_failed', 'Envio Fallido'), ('sent_to_sap', 'Enviado a SAP')],index=True)

    split_state = fields.Selection([
        ('block',_('Bloqueado')),
        ('approve',_('Aprobado')),
        ('dispatch',_('Despachado')),
        ('cancel',_('Cancelado')),
    ],string="States",translate=True,index=True)
    no_split_state = fields.Selection([
        ('quotation',_('Cotizacion')),
        ('sale',_('Orden de Venta')),
        ('sent_failed',_('Envio Fallido')),
        ('sent',_('Enviado a SAP')),
        ('cancel',_('Cancelado')),
    ],string="States",translate=True)

    @api.onchange('partner_shipping_id')
    def _onchange_pship_id(self):
        self.ec_dest_id = self.partner_shipping_id

    @api.depends('order_line','order_line.vbap_werks')
    @api.onchange('vbap_werks')
    def _onchange_vbap_werks(self):
        for line in self.order_line:
            line.vbap_werks = self.vbap_werks

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        res['validity_date'] = datetime.now()
        return res

    def SendOrder(self, credential, json):
        message = credential.user + ":" + credential.passwd
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic ' + base64_message
        }
        print(headers)
        data = str(json).encode('utf-8')
        base_url = credential.endpoint_pedidos
        req = requests.post(base_url, data=data, headers=headers)
        return req.text

    def format_date(self, the_date):
        if len(str(the_date)) <= 10:
            return datetime.strptime(str(the_date), "%Y-%m-%d").strftime("%d.%m.%Y")
        else:
            return datetime.strptime(str(the_date), "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")

    @api.depends('vbak_vkorg_id', 'state', 'sap_code', 'vbak_vkorg_id.direct_to_sap')
    @api.onchange('state')
    def _send_to_sap_onchange(self):
        if self.vbak_vkorg_id.direct_to_sap and self.state == 'sale' and not self.sap_code:
            self.send_to_sap()

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            rec.with_context(from_button=True)._send_to_sap_onchange()
            sps = self.env['stock.picking'].search([('origin', '=', rec.name)])
            sps.unlink()
        return res

    def create_sap_sales(self, result, json2):
        sap_sale = json.loads(result)
        _logger.info(isinstance(sap_sale, dict))
        _logger.info(type(sap_sale))
        if True:
            _logger.info("resultado encontrado")
            if sap_sale['enviarCrearPedido_Resp'] and sap_sale['enviarCrearPedido_Resp']['RESULTADO'] == 'OK' and json2['SIMULACION'] == 'N':
                _logger.info("simulacion N encontrado")
                for elem_doc_array in sap_sale['enviarCrearPedido_Resp']['ARRAY_DOCUMENTOS']:
                    _logger.info(elem_doc_array)
                    temp = dict()
                    if not self.pickup:
                        temp.update({'VBPA_PARVW': 'EM', 'VBPA_KUNNR': self.partner_shipping_id.sap_code})
                    else:
                        order_line = self.env['sale.order.line'].browse(
                            int(elem_doc_array['ARRAY_MERCADERIAS'][0]['IDLINEAODOO']))
                        temp.update({'VBPA_PARVW': 'EM', 'VBPA_KUNNR': order_line.vbap_werks.code})
                    position_list = list()
                    for pos in elem_doc_array['ARRAY_MERCADERIAS']:
                        order_line2 = self.env['sale.order.line'].browse(int(pos['IDLINEAODOO']))
                        position_list.append((0,0,{
                            'VBAP_MATNR': pos['VBAP_MATNR'],
                            'JEST_STAT': pos['JEST_STAT'],
                            'KONV_WAERS': order_line2.KONV_WAERS.code,
                            'VBAP_KWMENG': order_line2.product_uom_qty,
                            'VBAP_VRKME': order_line2.product_uom.sap_code,
                            'VBKD_BSTKD': self.name,
                        }))
                    val_date = ""
                    if self.validity_date:
                        val_date = self.validity_date.strftime("%d-%m-%Y")
                    vals = {
                        'VBAK_AUART': self.sap_document_type_id.code,
                        'VBAK_ZTERM': self.payment_term_id.sap_code,
                        'VBAK_ANGDT': self.start_date,
                        'VBAK_BNDDT': val_date.replace('-','.'),
                        'VBAK_VBELN': elem_doc_array['VBAK_VBELN'],
                        'VBAK_VKORG': elem_doc_array['VBAK_VKORG'],
                        'VBAK_VTWEG': elem_doc_array['VBAK_VTWEG'],
                        'VBAK_SPART': elem_doc_array['VBAK_SPART'],
                        'BLOCKED': elem_doc_array['BLOCKED'],
                        'VBUK_CMPSB': elem_doc_array['VBUK_CMPSB'],
                        'VBUK_CMPSF': elem_doc_array['VBUK_CMPSF'],
                        'VBUK_CMPSG': elem_doc_array['VBUK_CMPSG'],
                        'VBUK_CMGST': elem_doc_array['VBUK_CMGST'],
                        'VBAK_UPDKZ': 'I',
                        'sap_sales_interlocutor_ids': [
                            (0,0,{'VBPA_PARVW': 'SO', 'VBPA_KUNNR': self.partner_id.sap_code}),
                            (0, 0, {'VBPA_PARVW': 'RF', 'VBPA_KUNNR': self.partner_invoice_id.sap_code}),
                            (0, 0, temp)
                            ],
                        'sap_sales_position_ids': position_list
                    }
                    _logger.info(vals)
                    sap_sales_rec = self.env['sap.sales'].create(vals)
                    self.state = 'sent_to_sap'
                    print (sap_sales_rec)
            if sap_sale['enviarCrearPedido_Resp'] and sap_sale['enviarCrearPedido_Resp']['RESULTADO'] != 'OK' and json2['SIMULACION'] == 'N':
                self.state = 'sent_failed'
            if not sap_sale['enviarCrearPedido_Resp']:
                self.state = 'sent_failed'

            if sap_sale['enviarCrearPedido_Resp'] and self.sap_code and json2['SIMULACION'] == 'N':
                if elem_doc_array['BLOCKED'] == 'S':
                    self.state = 'done'
                else:
                    self.state = 'approved'
                foundf = True
                for line in self.order_line:
                    del_quant = sum(self.env['stock.move'].search([('sale_line_id', '=', line.id)]).mapped('product_uom_qty'))
                    if line.qty_delivered != del_quant:
                        foundf = False
                        pass
                if foundf:
                    self.split_state = 'dispatch'


    def send_to_sap(self):
        for rec in self:
            print (rec.validity_date)
            #if not rec.validity_date:
            #    raise UserError(_("please complete validity_date first"))

            from_button = self.env.context.get('from_button', False)

            token, credential = self.env['sap.ws.credentials'].Get_token()

            json = dict()
            if from_button:
                json.update({'SIMULACION':'N'})
            else:
                json.update({'SIMULACION': 'S'})

            if rec.pickup:
                json.update({'ENTREGA_EN_PLANTA': 'S'})
            else:
                json.update({'ENTREGA_EN_PLANTA': 'N'})

            json.update({'token': token})
            if rec.sap_document_type_id.code:
                json.update({'VBAK_AUART': rec.sap_document_type_id.code})
            if rec.vbak_vkorg_id.name:
                json.update({'VBAK_VKORG': rec.vbak_vkorg_id.code})
            if rec.vbak_vtweg_id.name:
                json.update({'VBAK_VTWEG': rec.vbak_vtweg_id.code})
            if rec.payment_term_id.sap_code:
                json.update({'VBAK_ZTERM': rec.payment_term_id.sap_code})
            if rec.name:
                json.update({'VBKD_BSTKD': rec.name})
            if rec.start_date:
                json.update({'VBAK_ANGDT': self.format_date(rec.start_date)})
            if rec.validity_date:
                json.update({'VBAK_BNDDT': self.format_date(rec.validity_date)})
            if rec.commitment_date:
                json.update({'VBEP_EDATU': self.format_date(rec.commitment_date)})
            if rec.partner_id.sap_code:
                json.update({'SOLICITANTE': rec.partner_id.sap_code})
            if rec.client_order_ref:
                json.update({'VBKD_BSTKD_OC': rec.client_order_ref})
            t1 = ""
            if rec.note:
                t1 = rec.note
            t2 = ""
            if rec.note_obs:
                t2 = rec.note_obs
            t3 = ""
            if rec.note_inv:
                t3 = rec.note_inv
            json.update({'ARRAY_TEXTOS': [
                {'TEXT_ID': '0012','TEXT_LINE': t1},
                {'TEXT_ID': 'Z008','TEXT_LINE': t2},
                {'TEXT_ID': 'Z009', 'TEXT_LINE': t3},
            ]})
            alist = list()
            for line in rec.order_line:
                temp = dict()
                temp2 = dict()
                if line.id:
                    temp.update({'IDLINEAODOO':line.id})
                if line.product_id.sap_code:
                    temp.update({'VBAP_MATNR': line.product_id.sap_code})
                if line.vbap_werks.code:
                    temp.update({'VBAP_WERKS': line.vbap_werks.code})
                if line.product_uom_qty:
                    temp.update({'VBAP_KWMENG': line.product_uom_qty})
                if line.product_uom.sap_code:
                    temp.update({'VBAP_VRKME': line.product_uom.sap_code})
                if self.pickup:
                    if line.vbap_werks.code:
                        temp.update({'DESTINATARIO': line.vbap_werks.code})
                else:
                    if line.DELIVERY_ADDRESS.sap_code:
                        temp.update({'DESTINATARIO': line.DELIVERY_ADDRESS.sap_code})
                if line.UTILIZACION:
                    temp.update({'UTILIZACION': line.UTILIZACION.sap_code})

                if line.manual_price:
                    temp.update({'PRECIO_MANUAL': 'S'})
                else:
                    temp.update({'PRECIO_MANUAL': 'N'})

                if line.kschl:
                    temp2.update({'KONV_KSCHL': line.kschl.mapped('name')})
                if line.manual_price:
                    temp2.update({'KONV_KBETR': line.price_unit})
                    temp2.update({'KONV_WAERS': line.KONV_WAERS.code})
                else:
                    temp2.update({'KONV_KBETR': ''})
                    temp2.update({'KONV_WAERS': ''})
                temp2.update({'KONV_KPEIN': ''})
                temp2.update({'KONV_KMEIN': ''})
                temp.update({'PRECIO':[temp2]})
                alist.append(temp)
            json.update({'ARRAY_MERCADERIAS': alist})

            _logger.info(json)
            result = self.SendOrder(credential,json)
            print (result)
            rec.create_sap_sales(result=result, json2=json)
            rec.write({'sap_message_sent': json,
                       'sap_message_recieved': result,
                       })

    def send_to_sap_web(self):
        for rec in self.sudo():
            rec.send_to_sap()
            sap_sale = json.loads(rec.sap_message_recieved)

            if 'ARRAY_DOCUMENTOS' in sap_sale['enviarCrearPedido_Resp'].keys():
                for doc in sap_sale['enviarCrearPedido_Resp']['ARRAY_DOCUMENTOS']:
                    for merc in doc['ARRAY_MERCADERIAS']:
                        line = self.env['sale.order.line'].browse(int(merc['IDLINEAODOO']))
                        if line:
                            line.sudo().write({
                                'price_unit': merc['KONV_KBETR'],
                                'KONV_WAERS': self.env['sap.waers'].sudo().search([('code', '=', merc['KONV_WAERS'])]).id
                            })
                            line.sudo()._compute_amount()

    def write(self, vals):
        for rec in self:
            carrier = self.env['delivery.carrier']
            if rec.carrier_id:
                carrier = rec.carrier_id
            if 'carrier_id' in vals.keys():
                carrier = self.env['delivery.carrier'].browse(vals['carrier_id'])
            if carrier.pickup:
                vals['pickup'] = True

        return super(SaleOrder, self).write(vals)

    #         if self.env.user.login == 'admin':
    #             if rec.state == 'sent_to_sap' or self.sap_code != False:
    #                 raise UserError(_("NO es posible editar el registro ya enviado a sap o con sap code"))
    #     return super(SaleOrder, self).write(vals)


class SaleOrderline(models.Model):
    _inherit = 'sale.order.line'

    kschl = fields.Many2many('kschl',string="Disc List")
    manual_price = fields.Boolean(string="Manual Price",default=False)
    vbap_werks = fields.Many2one('sap.werk',string="Delivering Plant")
    KONV_WAERS = fields.Many2one('sap.waers', string="KONV_WAERS",translate=True)
    DELIVERY_ADDRESS = fields.Many2one('res.partner',string="DELIVERY_ADDRESS",translate=True)
    root_partner_id = fields.Many2one(related="order_id.partner_id")
    prod_sap_code = fields.Char(related="product_id.sap_code",store=True,index=True)
    UTILIZACION = fields.Many2one('res.partner',string="Utilizacion")

    @api.depends('order_id','order_id.partner_shipping_id','product_id')
    @api.onchange('order_id','product_id')
    def _onchange_DELIVERY_ADDRESS(self):
        if not self.DELIVERY_ADDRESS:
           self.DELIVERY_ADDRESS = self.order_id.partner_shipping_id
           self.UTILIZACION = self.order_id.partner_shipping_id

    # @api.onchange('kschl')
    # def _onchange_kschl(self):
    #     self.discount = self.kschl.discount

    @api.depends('order_id','order_id.vbap_werks','product_id')
    @api.onchange('order_id','product_id')
    def _onchange_vbap_werks(self):
        if not self.vbap_werks:
            self.vbap_werks = self.order_id.vbap_werks
            self.KONV_WAERS = self.product_id.KONV_WAERS
    
    @api.model_create_multi
    def create(self, values):
        for vals in values:
            if 'product_id' in vals.keys():
                vals['KONV_WAERS'] = self.env['product.product'].browse(vals['product_id']).KONV_WAERS.id
        return super().create(values)

class BlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    vbak_vkorg_id = fields.Many2one('sap.vbak.vkorg',string="Sales Organizacion")
    vbak_vtweg_id = fields.Many2one('sap.vbak.vtweg',string="Distribution Channel")
    vbak_spart_id = fields.Many2one('sap.vbak.spart',string="Sector")
    vbuk_cmpsb = fields.Char(size=50,string="Credit Block (limit)")
    vbuk_cmpsf = fields.Char(size=50,string="Credit Block (due)")
    vbuk_cmpsg = fields.Char(size=50,string="Credit Block (old)")
    vbuk_cmgst = fields.Char(size=50,string="Credit Block (global)")
    ec_dest_id = fields.Many2one('res.partner',string="Economic Destiny")
    pickup = fields.Boolean(string="Pickup",translate=True)
    vbap_werks = fields.Many2one('sap.werk',string="Delivering Plant")
    sap_document_type_id = fields.Many2one('sap.vbak.auart',string="SAP Document Type",translate=True)
    start_date = fields.Date(string="Start Date",translate=True)
    sap_code = fields.Char(size=20,string="SAP Code",translate=True,index=True)
    note_obs = fields.Text(string="Observaciones",help="Observaciones",translate=True)
    state = fields.Selection(selection_add=[('sent_failed', 'Envio Fallido'), ('sent_to_sap', 'Enviado a SAP')],index=True)

    split_state = fields.Selection([
        ('block',_('Bloqueado')),
        ('approve',_('Aprobado')),
        ('dispatch',_('Despachado')),
        ('cancel',_('Cancelado')),
    ],string="States",translate=True,index=True)
    no_split_state = fields.Selection([
        ('quotation',_('Cotizacion')),
        ('sale',_('Orden de Venta')),
        ('sent_failed',_('Envio Fallido')),
        ('sent',_('Enviado a SAP')),
        ('cancel',_('Cancelado')),
    ],string="States",translate=True)

    @api.depends('order_line','order_line.vbap_werks')
    @api.onchange('vbap_werks')
    def _onchange_vbap_werks(self):
        for line in self.order_line:
            line.vbap_werks = self.vbap_werks

    # def write(self, vals):
    #     for rec in self:
    #         if self.env.user.login != 'admin':
    #             if rec.state == 'sent_to_sap' or self.sap_code != False:
    #                 raise UserError(_("NO es posible editar el registro ya enviado a sap o con sap code"))
    #     return super(BlanketOrder, self).write(vals)

class SaleOrderline(models.Model):
    _inherit = 'sale.blanket.order.line'

    kschl = fields.Many2many('kschl',string="Disc List")
    manual_price = fields.Boolean(string="Manual Price",default=True)
    vbap_werks = fields.Many2one('sap.werk',string="Delivering Plant")
    KONV_WAERS = fields.Many2one('sap.waers', string="KONV_WAERS",translate=True)
    DELIVERY_ADDRESS = fields.Many2one('res.partner',string="DELIVERY_ADDRESS",translate=True)
    root_partner_id = fields.Many2one(related="order_id.partner_id")

    @api.depends('order_id','order_id.partner_shipping_id','product_id')
    @api.onchange('order_id','product_id')
    def _onchange_DELIVERY_ADDRESS(self):
        if not self.DELIVERY_ADDRESS:
           self.DELIVERY_ADDRESS = self.order_id.partner_shipping_id

    @api.depends('order_id','order_id.vbap_werks','product_id')
    @api.onchange('order_id','product_id')
    def _onchange_vbap_werks(self):
        if not self.vbap_werks:
           self.vbap_werks = self.order_id.vbap_werks

    # @api.onchange('kschl')
    # def _onchange_kschl(self):
    #     self.discount = self.kschl.discount

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    pickup = fields.Boolean(string="Pickup",translate=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sap_code = fields.Char(size=20,string="SAP Code",translate=True)

class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    sap_code = fields.Char(size=20,string="SAP Code",translate=True)

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    sap_code = fields.Char(size=20,string="SAP Code",translate=True)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    pickup = fields.Boolean(string="Pickup", translate=True)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sap_code = fields.Char(size=40,string="sap code",translate=True)
    official_nr = fields.Char(size=40,string="Delivery Nr",translate=True)
