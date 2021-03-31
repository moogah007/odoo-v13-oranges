# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sap_ref = fields.Char(string="SAP Ref",translate=True)
    partner_address = fields.Char(related="partner_id.street",string="Address")
    state = fields.Selection(selection_add=[('approved', 'Ordenes Aprobadas'),('dispatched', 'Ordenes Despachadas')])