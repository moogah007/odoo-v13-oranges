import binascii
import logging
import tempfile

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class UploadUrlFile(models.TransientModel):
    _name = 'upload.url.file'
    _description = 'Upload Bulk Images Wizard'

    applied_object = fields.Selection([
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
        ('product', 'Product'),
        ('product_variants', 'Product Variants'),
    ], string='Applied Object', required=True, default='product')
    product_map_field = fields.Selection([
        ('product_id', 'Product Database Id'),
        ('product_name', 'Product Name'),
        ('default_code', 'Product Default Code'),
        ('ean13', 'Product EAN13 Barcode'),
    ], string='Select Map Field')
    partner_map_field = fields.Selection([
        ('partner_id', 'Partner Database Id'),
        ('partner_name', 'Partner Name'),
    ], string='Select Map Field')
    file_type = fields.Selection([
        ('csv', 'CSV File'),
        ('xls', 'XLS File')
    ], string='Select File Type', required=True, default='csv')
    csv_excel_file = fields.Binary(string='CSV/Excel File', required=True)
    file_name = fields.Char(string='File Name')

    @api.onchange('applied_object')
    def _onchange_applied_object(self):
        self.product_map_field = ''
        self.partner_map_field = ''

    def upload_images(self):
        # File : 'Mapped Field', 'image_url'
        for obj in self:
            if obj.product_map_field:
                map_field = obj.product_map_field
            elif obj.partner_map_field:
                map_field = obj.partner_map_field
            if obj.applied_object == 'supplier' and obj.file_type == 'csv':
                self.upload_images_supplier_csv(obj.csv_excel_file, map_field)
            elif obj.applied_object == 'supplier' and obj.file_type == 'xls':
                self.upload_images_supplier_xls(obj.csv_excel_file, map_field)
            elif obj.applied_object == 'customer' and obj.file_type == 'csv':
                self.upload_images_customer_csv(obj.csv_excel_file, map_field)
            elif obj.applied_object == 'customer' and obj.file_type == 'xls':
                self.upload_images_customer_xls(obj.csv_excel_file, map_field)
            elif obj.applied_object == 'product' and obj.file_type == 'csv':
                self.upload_images_product_csv(obj.csv_excel_file, map_field)
            elif obj.applied_object == 'product' and obj.file_type == 'xls':
                self.upload_images_product_xls(obj.csv_excel_file, map_field)
            elif obj.applied_object == 'product_variants' and obj.file_type == 'csv':
                self.upload_images_product_variants_csv(obj.csv_excel_file, map_field)
            elif obj.applied_object == 'product_variants' and obj.file_type == 'xls':
                self.upload_images_product_variants_xls(obj.csv_excel_file, map_field)
        return True

    def upload_images_supplier_csv(self, csv_excel_file, map_field):
        partner = self.env['res.partner']
        line_list = base64.decodestring(csv_excel_file).split(b'\n')
        record_list = [line.decode('ascii') for line in line_list if line]
        if record_list:
            # Skip Header Line
            record_list.pop(0)
            for line in record_list:
                try:
                    line = csv.reader(line.split(','))
                    content = [i[0] if i else '' for i in line]
                except Exception:
                    raise ValidationError('Make Sure File Is Comma Separated and other Details')
                if map_field == 'partner_id':
                    part = partner.browse(int(content[0]))
                    part.write({'image_url': content[1]})
                elif map_field == 'partner_name':
                    part = partner.search([('name', '=', content[0]), ('supplier_rank', '>', 0)])
                    if part:
                        part.write({'image_url': content[3]})
        return True

    def upload_images_supplier_xls(self, csv_excel_file, map_field):
        partner = self.env['res.partner']
        file_pointer = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        file_pointer.write(binascii.a2b_base64(csv_excel_file))
        file_pointer.seek(0)
        book = xlrd.open_workbook(file_pointer.name)
        sheet = book.sheet_by_index(0)
        for row_number in range(sheet.nrows):
            if row_number <= 0:
                # Skip Header Row
                continue
            else:
                line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_number)))
                if not line[0]:
                    # Skip Empty Line
                    continue
                if map_field == 'partner_id':
                    part = partner.browse(int(float(line[0])))
                    part.write({'image_url': line[1]})
                elif map_field == 'partner_name':
                    part = partner.search([('name', '=', line[0]), ('supplier_rank', '>', 0)])
                    if part:
                        part.write({'image_url': line[1]})
        return True

    def upload_images_customer_csv(self, csv_excel_file, map_field):
        partner = self.env['res.partner']
        line_list = base64.decodestring(csv_excel_file).split(b'\n')
        record_list = [line.decode('ascii') for line in line_list if line]
        if record_list:
            # Skip Header Line
            record_list.pop(0)
            for line in record_list:
                try:
                    line = csv.reader(line.split(','))
                    content = [i[0] if i else '' for i in line]
                except Exception:
                    raise ValidationError('Make Sure File Is Comma Separated and other Details')
                if map_field == 'partner_id':
                    part = partner.browse(int(content[0]))
                    part.write({'image_url': content[1]})
                elif map_field == 'partner_name':
                    part = partner.search([('name', '=', content[0]), ('customer_rank', '>', 0)])
                    if part:
                        part.write({'image_url': content[3]})
        return True

    def upload_images_customer_xls(self, csv_excel_file, map_field):
        partner = self.env['res.partner']
        file_pointer = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        file_pointer.write(binascii.a2b_base64(csv_excel_file))
        file_pointer.seek(0)
        book = xlrd.open_workbook(file_pointer.name)
        sheet = book.sheet_by_index(0)
        for row_number in range(sheet.nrows):
            if row_number <= 0:
                # Skip Header Row
                continue
            else:
                line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_number)))
                if not line[0]:
                    # Skip Empty Line
                    continue
                if map_field == 'partner_id':
                    part = partner.browse(int(float(line[0])))
                    part.write({'image_url': line[1]})
                elif map_field == 'partner_name':
                    part = partner.search([('name', '=', line[0]), ('customer_rank', '>', 0)])
                    if part:
                        part.write({'image_url': line[1]})
        return True

    def upload_images_product_csv(self, csv_excel_file, map_field):
        prod_tmpl = self.env['product.template']
        line_list = base64.decodestring(csv_excel_file).split(b'\n')
        record_list = [line.decode('ascii') for line in line_list if line]
        if record_list:
            # Skip Header Line
            record_list.pop(0)
            for line in record_list:
                try:
                    line = csv.reader(line.split(','))
                    content = [i[0] if i else '' for i in line]
                except Exception:
                    raise ValidationError('Make Sure File Is Comma Separated and other Details')
                try:
                    if map_field == 'product_id':
                        tmpl = prod_tmpl.browse(int(content[0]))
                        tmpl.write({'image_url': content[1]})
                    elif map_field == 'product_name':
                        tmpl = prod_tmpl.search([('name', '=', content[0])])
                        if tmpl:
                            tmpl.write({'image_url': content[1]})
                    elif map_field == 'default_code':
                        tmpl = prod_tmpl.search([('default_code', '=', content[0])])
                        if tmpl:
                            tmpl.write({'image_url': content[1]})
                    elif map_field == 'ean13':
                        tmpl = prod_tmpl.search([('ean13', '=', content[0])])
                        if tmpl:
                            tmpl.write({'image_url': content[1]})
                except Exception:
                    raise ValidationError('Make Sure Selected Mapping Field And Data Is Correct.')
        return True

    def upload_images_product_xls(self, csv_excel_file, map_field):
        prod_tmpl = self.env['product.template']
        file_pointer = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        file_pointer.write(binascii.a2b_base64(csv_excel_file))
        file_pointer.seek(0)
        book = xlrd.open_workbook(file_pointer.name)
        sheet = book.sheet_by_index(0)
        for row_number in range(sheet.nrows):
            if row_number <= 0:
                # Skip Header Row
                continue
            else:
                line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_number)))
                if not line[0]:
                    # Skip Empty Line
                    continue
                if map_field == 'product_id':
                    tmpl = prod_tmpl.browse(int(float(line[0])))
                    tmpl.write({'image_url': line[1]})
                elif map_field == 'product_name':
                    tmpl = prod_tmpl.search([('name', '=', line[0])])
                    if tmpl:
                        tmpl.write({'image_url': line[1]})
                elif map_field == 'default_code':
                    print("line[0] : ", line[0])
                    tmpl = prod_tmpl.search([('default_code', '=', line[0])])
                    if tmpl:
                        tmpl.write({'image_url': line[1]})
                elif map_field == 'ean13':
                    tmpl = prod_tmpl.search([('ean13', '=', line[0])])
                    if tmpl:
                        tmpl.write({'image_url': line[1]})
        return True

    def upload_images_product_variants_csv(self, csv_excel_file, map_field):
        prod_tmpl = self.env['product.product']
        line_list = base64.decodestring(csv_excel_file).split(b'\n')
        record_list = [line.decode('ascii') for line in line_list if line]
        if record_list:
            # Skip Header Line
            record_list.pop(0)
            for line in record_list:
                try:
                    line = csv.reader(line.split(','))
                    content = [i[0] if i else '' for i in line]
                except Exception:
                    raise ValidationError('Make Sure File Is Comma Separated and other Details')
                if map_field == 'product_id':
                    tmpl = prod_tmpl.browse(int(content[0]))
                    tmpl.write({'image_url': content[1]})
                elif map_field == 'product_name':
                    tmpl = prod_tmpl.search([('name', '=', content[0])])
                    if tmpl:
                        tmpl.write({'image_url': content[1]})
                elif map_field == 'default_code':
                    tmpl = prod_tmpl.search([('default_code', '=', content[0])])
                    if tmpl:
                        tmpl.write({'image_url': content[1]})
                elif map_field == 'ean13':
                    tmpl = prod_tmpl.search([('ean13', '=', content[0])])
                    if tmpl:
                        tmpl.write({'image_url': content[1]})
        return True

    def upload_images_product_variants_xls(self, csv_excel_file, map_field):
        product = self.env['product.product']
        file_pointer = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        file_pointer.write(binascii.a2b_base64(csv_excel_file))
        file_pointer.seek(0)
        book = xlrd.open_workbook(file_pointer.name)
        sheet = book.sheet_by_index(0)
        for row_number in range(sheet.nrows):
            if row_number <= 0:
                # Skip Header Row
                continue
            else:
                line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_number)))
                if not line[0]:
                    # Skip Empty Line
                    continue
                if map_field == 'product_id':
                    prod = product.browse(int(float(line[0])))
                    prod.write({'image_url': line[1]})
                elif map_field == 'product_name':
                    prod = product.search([('name', '=', line[0])])
                    if prod:
                        prod.write({'image_url': line[1]})
                elif map_field == 'default_code':
                    prod = product.search([('default_code', '=', line[0])])
                    if prod:
                        product.write({'image_url': line[1]})
                elif map_field == 'ean13':
                    prod = product.search([('ean13', '=', line[0])])
                    if prod:
                        prod.write({'image_url': line[1]})
        return True


class ImportImageUrlLog(models.Model):
    _name = 'import.image.url.log'
    _description = 'Import Images Log'

    object = fields.Char(string='Object', size=50, readonly=1)
    resource_id = fields.Integer(string='Resource', readonly=1)
    result = fields.Selection([('success', 'Success'), ('error', 'Error')], string='Result', readonly=1)
    error_message = fields.Text(string='Error Message', readonly=1)
