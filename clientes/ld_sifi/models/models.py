# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar
    
class ledesmaSapship(models.Model):
    _name = 'ledesma.sap.ship'
    _description = 'ledesma.sap.ship'

    name = fields.Char(string="Descripcion",translate=True)

class LedesmaSapPort(models.Model):
    _name = 'ledesma.sap.port'
    _description = 'ledesma.sap.port'

    name = fields.Char(string="Descripcion",translate=True)
    country_id = fields.Many2one('res.country',string="Pais",translate=True)
    type = fields.Selection([('origin','Origen'),('destination','Destino')],string="Tipo",translate=True)
    sap_center = fields.Char('Centro Sap',translate=True)
    active = fields.Boolean(string="Activo",translate=True)

class LedesmaSapPosAran(models.Model):
    _name = 'ledesma.sap.pos.aran'
    _description = 'ledesma.sap.pos.aran'

    name = fields.Char(string="Code",translate=True)
    retention = fields.Float(string="% Retencion",translate=True)
    refund = fields.Float(string="% Reembolso",translate=True)

class LedesmaSapPosAran(models.Model):
    _name = 'ledesma.sap.shipping'
    _description = 'ledesma.sap.shipping'

    name = fields.Char(string="Descripcion",translate=True)
    pallets_capacity = fields.Integer(string="Capacidad de Pallets",translate=True)

class ledesmaSapshipPrice(models.Model):
    _name = 'ledesma.sap.ship.price'
    _description = 'ledesma.sap.ship.price'

    name = fields.Char(string="Descripcion",translate=True)
    partner_id = fields.Many2one('res.partner',string="Naviera",translate=True,domain="[('supplier_rank', '>', 0)]")
    port_out_id = fields.Many2one('ledesma.sap.port', string="Puerto Salida", translate=True)
    port_in_id = fields.Many2one('ledesma.sap.port', string="Puerto Destino", translate=True)
    transport_id = fields.Many2one('ledesma.sap.shipping',string="Transporte",translate=True)
    shipping_cost = fields.Float(string="Costo Flete",translate=True)
    line_ids = fields.One2many('ledesma.sap.ship.price.line','ship_price_id',string="Lines",translate=True)

class ledesmaSapshipPriceLine(models.Model):
    _name = 'ledesma.sap.ship.price.line'
    _description = 'ledesma.sap.ship.price.line'

    ship_price_id = fields.Many2one('ledesma.sap.ship.price')
    product_id = fields.Many2one('product.product',string="Producto",translate=True)
    amount_price = fields.Float(string="Precio",translate=True)

class ledesmaSapCalibre(models.Model):
    _name = 'ledesma.sap.calibre'
    _description = 'ledesma.sap.calibre'

    name = fields.Char(string="Descripcion",translate=True)
    categ1_id = fields.Many2one('res.partner.category',string="Especie",translate=True)
    categ2_id = fields.Many2one('res.partner.category',string="Variedad",translate=True)
    categ3_id = fields.Many2one('res.partner.category',string="Tipo de Envase",translate=True)
    calibre_ue = fields.Integer(string="Calibre UE",translate=True)
    diameter_ue = fields.Char(string="Diametros UE",translate=True)
    diameter_ledesma = fields.Char(string="Diametros Ledesma",translate=True)
    qty = fields.Integer(string="Cantidad",translate=True)

class ledesmaTexts(models.Model):
    _name = 'ledesma.texts'
    _description = 'ledesma.texts'

    name = fields.Char(string="Nombre",translate=True)
    desc = fields.Text(string="Descripcion",translate=True)

class ledesmaSapCateg(models.Model):
    _name = 'ledesma.sap.categ'
    _description = 'ledesma.sap.categ'

    name = fields.Char(string="Categoria",translate=True)

class LedesmaSapCountermark(models.Model):
    _name = 'ledesma.sap.countermark'
    _description = 'ledesma.sap.countermark'

    name = fields.Char(string="Code",translate=True,index=True)
    cm_class = fields.Char(string="Class",translate=True)
    cm_pos = fields.Integer(string="Position",translate=True)
    cm_partner_id = fields.Many2one('res.partner',string="Customer Code",translate=True)
    cm_partner_name = fields.Char(string="Customer Name",translate=True)
    cm_product_id = fields.Many2one('product.product',string="Material",translate=True)

    cm_prod_type_id = fields.Many2one('product.product',string="Especie",translate=True)
    cm_prod_variety_id = fields.Many2one('product.product',string="Variedad",translate=True)
    cm_prod_mark_id = fields.Many2one('product.product',string="Marca",translate=True)
    cm_prod_env_type_id = fields.Many2one('product.product',string="Tipo de Envase",translate=True)

    cm_real_categ_id = fields.Many2one('ledesma.sap.categ',string="Real Category",translate=True)
    cm_label_categ_id = fields.Many2one('ledesma.sap.categ',string="Label Category",translate=True)
    cm_calibre_from_id = fields.Many2one('ledesma.sap.calibre',string="Calibre Desde",trasnlate=True)
    cm_calibre_to_id = fields.Many2one('ledesma.sap.calibre',string="Calibre Hasta",trasnlate=True)

class LedesmaSapAssurance(models.Model):
    _name = 'ledesma.sap.assurance'
    _description = 'ledesma.sap.assurance'

    name = fields.Char(string="Name",translate=True)
    perc = fields.Float(string="Percentage",translate=True)

class LedesmaSapEnvelope(models.Model):
    _name = 'ledesma.sap.envelope'
    _description = 'ledesma.sap.envelope'

    name = fields.Char(string="Codigo CM",translate=True)
    desc = fields.Float(string="Descripcion",translate=True)
    nett = fields.Float(string="Peso Neto",translate=True)
    gross = fields.Float(string="Peso Bruto",translate=True)
    pallet_cont_capacity = fields.Float(string="Capacidad Pallet Contenedor",translate=True)
    pallet_cellar_capacity = fields.Float(string="Capacidad Pallet Bodega",translate=True)


