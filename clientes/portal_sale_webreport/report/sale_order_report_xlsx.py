# -*- coding: utf-8 -*-
from odoo import models, _


class SaleOrderReportXlsx(models.AbstractModel):
    _name = "report.portal_sale_webreport.sale_order_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Sale Order XLSX Report"

    def generate_xlsx_report(self, workbook, data, order_id):
        decimal_precision = self.env['decimal.precision'].precision_get('Stock Weight') or 2

        order_id.ensure_one()
        order_id = order_id.sudo()
        sheet = workbook.add_worksheet("Report")
        bold = workbook.add_format({"bold": True})
        row_idx = 0

        sheet.write(row_idx, 0, _('Reference'), bold)
        sheet.write(row_idx, 1, _(order_id.client_order_ref), )
        sheet.write(row_idx, 3, _('Term. Pago'), bold)
        sheet.write(row_idx, 4, _(order_id.payment_term_id.name) or '', )
        row_idx += 1

        sheet.write(row_idx, 0, _('Orden'), bold)
        sheet.write(row_idx, 1, _(order_id.name), )
        sheet.write(row_idx, 3, _('Validez'), bold)
        sheet.write(row_idx, 4, _((str(order_id.start_date) or '') + ' to ' + (str(order_id.validity_date) or '')), )
        row_idx += 1

        sheet.write(row_idx, 0, _('Customer'), bold)
        sheet.write(row_idx, 1, _(order_id.partner_id.name) or '', )
        sheet.write(row_idx, 3, _('Destino'), bold)
        sheet.write(row_idx, 4, _(order_id.partner_shipping_id.name) or '', )

        row_idx += 1
        sheet.write(row_idx, 1, _(order_id.partner_id.l10n_latam_identification_type_id.name or ''), )
        row_idx += 1
        sheet.write(row_idx, 1, _(order_id.partner_id.vat or ''), )

        row_idx += 3

        headers = [_('Producto'), _('Confirmado'), _('Entregado'), _('Pendiente'), _('Rechazado')]
        for h in headers:
            sheet.write(row_idx, headers.index(h), h, bold)
        row_idx += 1

        for line in order_id.order_line:
            sheet.write(row_idx, 0, line.product_id.name, )
            sheet.write(row_idx, 1, round(line.product_uom_qty, decimal_precision), )
            sheet.write(row_idx, 2, round(line.qty_delivered, decimal_precision), )
            sheet.write(row_idx, 3, round(line.get_pending_qty(), decimal_precision), )
            sheet.write(row_idx, 4, round(line.get_rejected_qty(), decimal_precision), )
            row_idx += 1


class SaleOrderLinkedReportXlsx(models.AbstractModel):
    _name = "report.portal_sale_webreport.sale_order_linked_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Sale Order XLSX Report"

    def generate_xlsx_report(self, workbook, data, order_id):
        decimal_precision = self.env['decimal.precision'].precision_get('Stock Weight') or 2

        order_id.ensure_one()
        order_id = order_id.sudo()
        sheet = workbook.add_worksheet("Report")
        bold = workbook.add_format({"bold": True})
        row_idx = 0

        sheet.write(row_idx, 0, _('Reference'), bold)
        sheet.write(row_idx, 1, _(order_id.client_order_ref), )
        sheet.write(row_idx, 3, _('Term. Pago'), bold)
        sheet.write(row_idx, 4, _(order_id.payment_term_id.name or ''), )
        row_idx += 1

        sheet.write(row_idx, 0, _('Orden'), bold)
        sheet.write(row_idx, 1, _(order_id.name), )
        sheet.write(row_idx, 3, _('Validez'), bold)
        sheet.write(row_idx, 4, _((str(order_id.start_date) or '') + ' to ' + (str(order_id.validity_date) or '')), )
        row_idx += 1

        sheet.write(row_idx, 0, _('Customer'), bold)
        sheet.write(row_idx, 1, _(order_id.partner_id.name or ''), )
        # sheet.write(row_idx, 3, 'Destination', bold)
        # sheet.write(row_idx, 4, order_id.partner_shipping_id.name or '', )

        row_idx += 1
        sheet.write(row_idx, 1, _(order_id.partner_id.l10n_latam_identification_type_id.name or ''), )
        row_idx += 1
        sheet.write(row_idx, 1, _(order_id.partner_id.vat or ''), )

        row_idx += 3

        headers = [_('Producto'), _('Confirmado'), _('Entregado'), _('Pendiente'), _('Rechazado')]
        for h in headers:
            sheet.write(row_idx, headers.index(h), h, bold)

        linked_product_lines_dict = order_id.get_linked_report_data()
        for line in linked_product_lines_dict:
            row_idx += 1
            sheet.write(row_idx, 0, linked_product_lines_dict[line]['product_name'], )
            sheet.write(row_idx, 1, round(linked_product_lines_dict[line]['confirmed_quantities'], decimal_precision), )
            sheet.write(row_idx, 2, round(linked_product_lines_dict[line]['delivered_quantities'], decimal_precision), )
            sheet.write(row_idx, 3, round(linked_product_lines_dict[line]['pending_quantities'], decimal_precision), )
            sheet.write(row_idx, 4, round(linked_product_lines_dict[line]['rejected_quantities'], decimal_precision), )
