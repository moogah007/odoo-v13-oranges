# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleBlanketOrder(models.Model):
    _inherit = 'sale.blanket.order'

    # VBKD_BSTKD = fields.Char(size=10, string="Main Order No.", translate=True)
    #BVAP_ABGRU = fields.Many2one('sale.order', string="Main Order No.", translate=True)
    VBKD_BSTKD = fields.Many2one('sale.order', string="Main Order No", translate=True)
    is_admin = fields.Boolean(string="Is Admin?", compute="_compute_is_admin")

    def _compute_is_admin(self):
        for rec in self:
            if rec.env.user.has_group('base.group_system'):
                rec.is_admin = True
            else:
                rec.is_admin = False

    def get_linked_report_data(self):
        SaleBlanketOrder = self.env['sale.blanket.order']
        self.ensure_one()
        order_id = self.sudo()
        if order_id.VBKD_BSTKD:
            linked_order_ids = SaleBlanketOrder.search([
                ('VBKD_BSTKD', '!=', False),
                ('VBKD_BSTKD', '=', order_id.VBKD_BSTKD.id)
            ])
        else:
            linked_order_ids = self.sudo()

        linked_product_lines_dict = {}

        for linked_order_id in linked_order_ids:
            for line_id in linked_order_id.order_line.sudo():
                if line_id.product_id.id not in linked_product_lines_dict:
                    linked_product_lines_dict.update({
                        line_id.product_id.id:
                            {
                                'product_id': line_id.product_id.id,
                                'product_name': line_id.product_id.name,
                                'confirmed_quantities': line_id.product_uom_qty,
                                'referenced_quantities': line_id.get_reference_qty(),
                                'delivered_quantities': line_id.delivered_uom_qty,
                                'rejected_quantities': line_id.get_rejected_qty(),
                                'pending_quantities': line_id.get_pending_qty()
                            }
                    })
                else:
                    linked_product_lines_dict[line_id.product_id.id]['confirmed_quantities'] += line_id.product_uom_qty
                    linked_product_lines_dict[line_id.product_id.id]['referenced_quantities'] += line_id.get_reference_qty()
                    linked_product_lines_dict[line_id.product_id.id]['delivered_quantities'] += line_id.delivered_uom_qty
                    linked_product_lines_dict[line_id.product_id.id]['pending_quantities'] += line_id.get_pending_qty()
                    linked_product_lines_dict[line_id.product_id.id]['rejected_quantities'] += line_id.get_rejected_qty()

        return linked_product_lines_dict


class SaleBlanketOrderLine(models.Model):
    _inherit = 'sale.blanket.order.line'

    BVAP_ABGRU = fields.Char(size=25, string="Rejected", translate=True)

    def get_reference_qty(self):
        if self.BVAP_ABGRU:
            return 0
        else:
            return self.ordered_uom_qty - self.delivered_uom_qty

    def get_rejected_qty(self):
        if self.BVAP_ABGRU:
            return self.product_uom_qty - self.delivered_uom_qty
        else:
            return 0

    def get_pending_qty(self):
        return self.product_uom_qty - self.get_reference_qty() - self.get_rejected_qty() - self.delivered_uom_qty
