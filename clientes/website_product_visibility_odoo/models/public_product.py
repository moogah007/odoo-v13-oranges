from odoo import api, models, fields
from mock.mock import self


class public_product(models.Model):
    _name = 'public.product'

    test = fields.Boolean("TEST")
    public_visible_product_ids = fields.Many2many('product.template', 'public_product_rel', 'public_id', 'product_id', string='Products')
    public_visible_category_ids = fields.Many2many('product.category', 'public_categ_rel', 'public_id', 'categ_id', string="Product Category")

    @api.model
    def default_get(self, fields):
        result = super(public_product, self).default_get(fields)
        public_product_id = self.search([], limit=1, order="id desc")
        if public_product_id:
            public_visible_product_ids = [visible_prod.id for visible_prod in public_product_id.public_visible_product_ids]
            public_visible_category_ids = [visible_categ.id for visible_categ in public_product_id.public_visible_category_ids]
            result.update({'public_visible_product_ids': [(6, 0, public_visible_product_ids)]})
            result.update({'public_visible_category_ids': [(6, 0, public_visible_category_ids)]})
        return result

    def add_all_product(self):
        public_visible_product_ids = [prod.id for prod in self.env['product.template'].search([])]
        if public_visible_product_ids:
            self.public_visible_product_ids = public_visible_product_ids
        return True

    def add_all_category(self):
        public_visible_category_ids = [categ.id for categ in self.env['product.category'].search([])]
        if public_visible_category_ids:
            self.public_visible_category_ids = public_visible_category_ids
        return True

    def write(self, vals):
        res = super(public_product, self).write(vals)
        partner = self.env.ref('base.public_partner')
        partner_vals = {
            'visible_product_ids': self.public_visible_product_ids,
            'visible_category_ids': self.public_visible_category_ids
        }
        partner.update(partner_vals)
        return res
