# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar

class ResPartner(models.Model):
    _inherit = 'res.partner'

    bonus = fields.Float(string="Comision",translate=True)
    sale_cond_id = fields.Many2one('account.incoterms',string="Sale Cond",translate=True)
    payment_cond_id = fields.Many2one('account.incoterms',string="Condicion de Pago",translate=True)
    sale_bonus_cond_id = fields.Many2one('account.incoterms',string="Bonus Sale Cond",translate=True)
    cm_code = fields.Char(string="Countermark Code",translate=True)

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    type_ledesma = fields.Selection([
        ('representante', 'Representante'),
        ('despachante', 'Despachante')],
        strng="Categoria Ledesma",
    )

class BlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    contract_nr = fields.Char(string="Nro Contrato")
    year_only = fields.Char(string="Campania",translate=True)
    inv_partner_id = fields.Many2one('res.partner',string="Invoice Client",
        translate=True,domain="[('customer_rank', '>', 0)]")
    purchase_order = fields.Char(string="Purchase Order",translate=True)

    def _get_domain_rep(self):
        tags = self.env['res.partner.category'].search([('type_ledesma', '=', 'representante')])
        return [('category_id', 'in', tags)]

    representative_id = fields.Many2one('res.partner',string="Representante",domain=_get_domain_rep)
    bonus = fields.Float(string="Comision",translate=True)
    sale_bonus_cond_id = fields.Many2one('account.incoterms',string="Bonus Sale Cond",translate=True)
    contract_type = fields.Selection(
        [('agreed_price','Precio Firme'),('review_price','Precios Revisables'),('consig','En Consignacion')],
        string="Tipo de Contrato",
        translate=True,
    )
    payment_cond_id = fields.Many2one('account.incoterms',string="Payment Cond",translate=True)
    sale_cond_id = fields.Many2one('account.incoterms',string="Sale Cond",translate=True)
    orig_port_id = fields.Many2one('ledesma.sap.port',string="Puerto de Origan",translate=True)
    dest_port_id = fields.Many2one('ledesma.sap.port',string="Puerto de Destino",translate=True)
    etd = fields.Date(string="ETD",translate=True)
    pallets_qty = fields.Integer(string="Total de Pallets",translate=True,compute="_compute_p_qty")

    terms_conds_id = fields.Many2one('ledesma.texts',string="Terminos y condiciones template",translate=True)
    terms_conds_text = fields.Text(strin="Detail",translate=True,related="terms_conds_id.desc",readonly=True)
    important_id = fields.Many2one('ledesma.texts',string="Importante",translate=True)
    important_text = fields.Text(string="Important",translate=True,related="important_id.desc",readonly=True)

    @api.depends('order_line','order_line.product_uom_qty')
    def _compute_p_qty(self):
        for rec in self:
            tot = 0
            for line in rec.order_line:
                tot += line.product_uom_qty
            rec.pallets_qty = tot


    @api.onchange('partner_id')
    def _onchange_partner_ledesma(self):
        self.bonus = self.partner_id.bonus
        self.sale_bonus_cond_id = self.partner_id.sale_bonus_cond_id.id
        self.sale_cond_id = self.partner_id.sale_cond_id.id
        self.payment_cond_id = self.partner_id.payment_cond_id.id


class BlanketOrderLine(models.Model):
    _inherit = 'sale.blanket.order.line'

    countermark_id = fields.Many2one('ledesma.sap.countermark',string="Contramarca",translate=True)

    prod_type_id = fields.Many2one('product.product',string="Especie",translate=True)
    prod_variety_id = fields.Many2one('product.product',string="Variedad",translate=True)
    prod_mark_id = fields.Many2one('product.product',string="Marca",translate=True)
    prod_env_type_id = fields.Many2one('product.product',string="Tipo de Envase",translate=True)
    prod_origin_id = fields.Many2one('product.product',string="Origen",translate=True)
    fruit_type = fields.Selection(
        [('owned','Propia'),('resale','Reventa'),('rented','Arriendo')],
        string="Tipo de Fruta",
        translate=True,
    )
    week_from = fields.Integer(string="Semana Desde",translate=True)
    week_to = fields.Integer(string="Semana Hasta",translate=True)
    date_from = fields.Date(string="Fecha Desde",translate=True,readonly=True)
    date_to = fields.Date(string="Fecha Hasta",translate=True,readonly=True)

    @api.onchange('week_from','week_to')
    def _onchange_week(self):
        self.date_from = False
        self.date_to = False
        if self.week_from:
            pass

    quality = fields.Selection(
        [('superior','Superior'),('chosen','Eeegido'),('comercial','Comercial')],
        string="Quality",
        translate=True,
    )
    quality_perc = fields.Char(string="% Quality",translate=True)
    calibre_from = fields.Many2one('ledesma.sap.calibre',string="Calibre Desde",trasnlate=True)
    calibre_to = fields.Many2one('ledesma.sap.calibre',string="Calibre Hasta",trasnlate=True)
    box_price = fields.Float(string="Precio por Caja",translate=True)
    ton_price = fields.Float(string="Precio por Tonelada",translate=True)
    stickers = fields.Selection(
        [('si','SI'),('no','NO')],
        string="Stickers",
        translate=True,
    )
    stickers_obs = fields.Char(string="Obs Stickers",translate=True)
    wrap_paper = fields.Selection(
        [('si','SI'),('no','NO')],
        string="Wrap Paper",
        translate=True,
    )
    sulf_obs = fields.Char(string="Obs Sulfito",translate=True)
    real_categ_id = fields.Many2one('ledesma.sap.categ',string="Real Category",translate=True)
    label_categ_id = fields.Many2one('ledesma.sap.categ',string="Label Category",translate=True)

    @api.depends('order_id','prod_env_type_id','real_categ_id','calibre_from','calibre_to','order_id')
    @api.onchange('order_id','prod_env_type_id','real_categ_id','calibre_from','calibre_to','order_id')
    def _create_countermark(self):
        rec = self
        str_cm = str(rec.order_id.partner_id.cm_code)[0:3] + \
                 str(rec.prod_env_type_id.name)[0:2] + \
                 str(rec.real_categ_id.code)[0:1] + \
                 str(rec.calibre_from.calibre_ue)[0:1] + \
                 str(rec.calibre_to.calibre_ue)[0:1] + \
                 str(rec.order_id.dest_port_id.country_id.code)[0:2]
        cm = self.env['ledesma.sap.countermark'].search([('name', '=', str_cm)])
        if not cm:
            cm = self.env['ledesma.sap.countermark'].create({
                'name': str_cm,
                'cm_class': 'EMPAQ_PROP_FRUTA',
                'cm_pos': '10',
                'cm_partner_id': rec.partner_id.id,
                'cm_partner_name': rec.partner_id.name,
                'cm_product_id': rec.product_id.id,
                'cm_prod_type_id': rec.prod_type_id.id,
                'cm_prod_variety_id': rec.prod_variety_id.id,
                'cm_prod_mark_id': rec.prod_mark_id.id,
                'cm_prod_env_type_id': rec.prod_env_type_id.id,
                'cm_real_categ_id': rec.real_categ_id.id,
                'cm_label_categ_id': rec.label_categ_id.id,
                'cm_calibre_from_id': rec.calibre_from.id,
                'cm_calibre_to_id': rec.calibre_to.id,
            })
        rec.countermark_id = cm.id
