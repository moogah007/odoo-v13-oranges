from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    visible_public_prod_categ_too = fields.Boolean("Visible Public Product And Categroy Too",
                                                   help="On Webshop Visible Registered User Product Plus All Public Product")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        Param = self.env['ir.config_parameter'].sudo()
        Param.set_param("website_product_visibility_odoo.visible_public_prod_categ_too", (self.visible_public_prod_categ_too or False))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(visible_public_prod_categ_too=params.get_param('website_product_visibility_odoo.visible_public_prod_categ_too', default=False))
        return res
