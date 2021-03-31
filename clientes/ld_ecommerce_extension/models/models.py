# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar


class SaleBlanketOrder(models.Model):
    _inherit = 'sale.blanket.order'

    client_order_ref = fields.Char(string="client order ref")

    def get_portal_url(self):
        portal_link = "%s/?db=%s" % (self.env['ir.config_parameter'].sudo().get_param('web.base.url'), self.env.cr.dbname)
        return portal_link

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_carrier_quotation(self, force_carrier_id=None):
        res = super(SaleOrder, self)._check_carrier_quotation(force_carrier_id)
        self.ensure_one()
        self._remove_delivery_line()
        return res

# class Website(models.Model):
#     _inherit = 'website'
#
#     def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
#         order = super(Website, self).sale_get_order(force_create,code,update_pricelist,force_pricelist)
#         if update_pricelist == True:
#             order.send_to_sap_web()
#         return order

class MailingList(models.Model):
    _inherit = 'mailing.list'

    def _default_toast_content(self):
        return _('<p>Thanks for subscribing!</p>')
