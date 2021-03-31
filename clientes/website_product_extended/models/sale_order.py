# -*- coding: utf-8 -*-
# Copyright 2020 Ketan Kachhela <l.kachhela28@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cart_categ_qty = fields.Integer(compute='_compute_cart_categ_qty', string='Cart Quantity')

    @api.depends('order_line')
    def _compute_cart_categ_qty(self):
        for order in self:
            order.cart_categ_qty = len(order.order_line.mapped('product_id'))
