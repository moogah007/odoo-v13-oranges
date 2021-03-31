# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ReportPortalLinkedSaleorder(models.AbstractModel):
    _name = 'report.portal_sale_webreport.report_portal_linked_saleorder'
    _description = 'Get hash integrity result as PDF.'

    @api.model
    def _get_report_values(self, docids, data=None):
        SaleOrder = self.env['sale.order']
        order_id = SaleOrder.browse(docids)
        linked_product_lines_dict = order_id.get_linked_report_data()

        return {
            'doc_ids': docids,
            'doc_model': self.env['sale.order'],
            'data': data,
            'docs': self.env['sale.order'].browse(docids),
            'linked_product_lines_dict': linked_product_lines_dict
        }
