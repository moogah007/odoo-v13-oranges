from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

import requests
import logging
_logger = logging.getLogger(__name__)

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class Partner(models.Model):
    _inherit = 'res.partner'

    image_url = fields.Char('IMAGE URL:')

    def write(self, vals):
        for obj in self:
            if vals.get('image_url'):
                if obj.customer_rank > 0:
                    object = 'Customer'
                elif obj.supplier_rank > 0:
                    object = 'Supplier'
                else:
                    object = 'Contact'
                log_val = {
                    'object': object,
                    'resource_id': int(obj.id),
                    'result': 'success',
                }
                try:
                    # binary_data = tools.image_resize_image_big(base64.b64encode(requests.get(vals.get('image_url')).content))
                    # vals.update({'image': binary_data})
                    vals.update({'image_1920': base64.b64encode(requests.get(vals.get('image_url')).content)})
                except Exception as e:
                    self.pool.get('import.image.url.log')
                    log_val.update({
                        'result': 'error',
                        'error_message': str(e),
                    })
                self.env['import.image.url.log'].create(log_val)
        return super(Partner, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('image_url'):
            if vals.get('customer'):
                object = 'Customer'
            elif vals.get('supplier'):
                object = 'Supplier'
            else:
                object = 'Contact'
            log_val = {
                'object': object,
                'resource_id': None,
                'result': 'success',
            }
            try:
                # binary_data = tools.image_resize_image_big(base64.b64encode(requests.get(vals.get('image_url')).content))
                # vals.update({'image': binary_data})
                vals.update({'image_1920': base64.b64encode(requests.get(vals.get('image_url')).content)})
            except Exception as e:
                self.pool.get('import.image.url.log')
                log_val.update({
                    'result': 'error',
                    'error_message': str(e),
                })
            self.env['import.image.url.log'].create(log_val)
        return super(Partner, self).create(vals)
