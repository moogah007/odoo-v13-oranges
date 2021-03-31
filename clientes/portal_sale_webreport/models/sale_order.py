# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # VBKD_BSTKD = fields.Char(size=25, string="Main Order No", translate=True)
    VBKD_BSTKD = fields.Many2one('sale.order', string="Main Order No (Order)", translate=True)
    is_admin = fields.Boolean(string="Is Admin?", compute="_compute_is_admin")

    def _compute_is_admin(self):
        for rec in self:
            if rec.env.user.has_group('base.group_system'):
                rec.is_admin = True
            else:
                rec.is_admin = False

    def get_linked_report_data(self):
        SaleOrder = self.env['sale.order']
        self.ensure_one()
        order_id = self.sudo()
        if order_id.VBKD_BSTKD:
            linked_order_ids = SaleOrder.sudo().search([
                ('VBKD_BSTKD', '!=', False),
                ('VBKD_BSTKD', '=', order_id.VBKD_BSTKD.id)
            ])
        else:
            linked_order_ids = self.sudo()

        linked_product_lines_dict = {}

        for linked_order_id in linked_order_ids:
            for line_id in linked_order_id.order_line:
                if line_id.product_id.id not in linked_product_lines_dict:
                    linked_product_lines_dict.update({
                        line_id.product_id.id:
                            {
                                'product_id': line_id.product_id.id,
                                'product_name': line_id.product_id.name,
                                'confirmed_quantities': line_id.product_uom_qty,
                                'delivered_quantities': line_id.qty_delivered,
                                'pending_quantities': line_id.get_pending_qty(),
                                'rejected_quantities': line_id.get_rejected_qty()
                            }
                    })
                else:
                    linked_product_lines_dict[line_id.product_id.id]['confirmed_quantities'] += line_id.product_uom_qty
                    linked_product_lines_dict[line_id.product_id.id]['delivered_quantities'] += line_id.qty_delivered
                    linked_product_lines_dict[line_id.product_id.id]['pending_quantities'] += line_id.get_pending_qty()
                    linked_product_lines_dict[line_id.product_id.id]['rejected_quantities'] += line_id.get_rejected_qty()

        return linked_product_lines_dict


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    BVAP_ABGRU = fields.Char(size=25, string="Rejected", translate=True)

    def get_rejected_qty(self):
        if self.BVAP_ABGRU:
            return self.product_uom_qty - self.qty_delivered
        else:
            return 0

    def get_pending_qty(self):
        return self.product_uom_qty - self.get_rejected_qty() - self.qty_delivered
