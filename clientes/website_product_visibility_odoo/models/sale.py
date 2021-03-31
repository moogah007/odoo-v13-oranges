from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # Added Product to visible_product_ids from Sale Order Line
        result = super(SaleOrder, self).action_confirm()
        visible_product_ids = []
        for sale_order in self:
            if sale_order.partner_id.add_product_from_history:
                for line in sale_order.order_line:
                    if not line.product_id.product_tmpl_id in self.partner_id.visible_product_ids:
                        visible_product_ids.append((4, line.product_id.product_tmpl_id.id))
            sale_order.partner_id.visible_product_ids = visible_product_ids
        return result
