from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import logging
import requests

_logger = logging.getLogger(__name__)
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    image_url = fields.Char('IMAGE URL:')

    @api.model
    def create(self, vals):
        if vals.get('image_url'):
            log_val = {
                'object': 'Product Variants',
                'resource_id': None,
                'result': 'success',
            }
            try:
                # binary_data = tools.image_resize_image_big(base64.b64encode(requests.get(vals.get('image_url')).content))
                # vals.update({'image': binary_data})
                vals.update({'image_1920': base64.b64encode(requests.get(vals.get('image_url')).content)})
            except Exception as e:
                log_val.update({
                    'result': 'error',
                    'error_message': str(e),
                })
            self.env['import.image.url.log'].create(log_val)
        return super(ProductProduct, self).create(vals)

    def write(self, values):
        ''' Store the standard price change in order to be able to retrieve the cost of a product for a given date'''
        for obj in self:
            if values.get('image_url'):
                log_val = {
                    'object': 'Product Variants',
                    'resource_id': obj.id,
                    'result': 'success',
                }
                try:
                    # binary_data = tools.image_resize_image_big(base64.b64encode(requests.get(values.get('image_url')).content))
                    # values.update({'image': binary_data})
                    values.update({'image_1920': base64.b64encode(requests.get(values.get('image_url')).content)})
                except Exception as e:
                    log_val.update({
                        'result': 'error',
                        'error_message': str(e),
                    })
                self.env['import.image.url.log'].create(log_val)

        return super(ProductProduct, self).write(values)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    image_url = fields.Char('IMAGE URL:')

    def write(self, vals):
        for obj in self:
            if vals.get('image_url'):
                log_val = {
                    'object': 'Product',
                    'resource_id': obj.id,
                    'result': 'success',
                }
                try:
                    # binary_data = tools.image_resize_image_big(base64.b64encode(requests.get(vals.get('image_url')).content))
                    # vals.update({'image': binary_data})
                    img_data = base64.b64encode(requests.get(vals.get('image_url')).content)
                    print("img_data : \n\n", img_data)
                    vals.update({'image_1920': img_data})
                except Exception as e:
                    log_val.update({
                        'result': 'error',
                        'error_message': str(e),
                    })
                self.env['import.image.url.log'].create(log_val)
        return super(ProductTemplate, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('image_url'):
            log_val = {
                'object': 'Product',
                'resource_id': None,
                'result': 'success',
            }
            try:
                # binary_data = tools.image_resize_image_big(base64.b64encode(requests.get(vals.get('image_url')).content))
                # vals.update({'image': binary_data})
                vals.update({'image_1920': base64.b64encode(requests.get(vals.get('image_url')).content)})
            except Exception as e:
                log_val.update({
                    'result': 'error',
                    'error_message': str(e),
                })
            self.env['import.image.url.log'].create(log_val)
        return super(ProductTemplate, self).create(vals)

