from odoo import api, fields, models


class ProductHistory(models.TransientModel):
    _name = 'product.history'

    product_ids = fields.One2many('product.history.line', 'product_history_id', string="History Line")

    @api.model
    def default_get(self, fields):
        rec = super(ProductHistory, self).default_get(fields)
        if str(self._context.get('active_model')) == 'res.partner':
            product_ids = []
            for order in self.env['sale.order'].search([('partner_id', '=', self._context.get('active_id'))]):
                for line in order.order_line:
                    product_ids.append(line.product_id.product_tmpl_id.id)
            product_ids = list(set(product_ids))
            rec['product_ids'] = [(0, 0, {'product_id': product_id}) for product_id in product_ids]
        return rec

    def button_add_product(self):
        if str(self._context.get('active_model')) == 'res.partner':
            product_list = []
            partner = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
            for product_line in self.product_ids:
                if product_line.product_id.id not in partner.visible_product_ids.ids:
                    product_list.append(product_line.product_id.id)
            product_list = list(set(product_list))
            if product_list:
                partner.write({'visible_product_ids': [(4, prod) for prod in product_list]})


class ProductHistoryLine(models.TransientModel):
    _name = 'product.history.line'
    product_history_id = fields.Many2one('product.history', string="Product History")
    product_id = fields.Many2one("product.template", string="Product")
