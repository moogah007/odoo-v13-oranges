from odoo import api, models, fields


class res_partner(models.Model):
    _inherit = "res.partner"

    add_product_from_history = fields.Boolean('In Future Auto Add Product From SO')
    visible_product_ids = fields.Many2many('product.template', 'partner_product_rel', 'partner_id', 'product_id', string='Visible Products')
    visible_category_ids = fields.Many2many('product.category', 'partner_categ_rel', 'partner_id', 'categ_id', string="Visible Product Category")

    def add_all_product(self):
        visible_product_ids = [prod.id for prod in self.env['product.template'].search([])]
        if visible_product_ids:
            self.visible_product_ids = visible_product_ids

    def add_all_category(self):
        visible_category_ids = [categ.id for categ in self.env['product.category'].search([])]
        if visible_category_ids:
            self.visible_category_ids = visible_category_ids
        return True
