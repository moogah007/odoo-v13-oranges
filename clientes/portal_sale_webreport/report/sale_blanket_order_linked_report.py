# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ReportPortalLinkedSaleBlanketOrder(models.AbstractModel):
    _name = 'report.portal_sale_webreport.rprt_prtl_lnkd_sale_bankt_ordr'
    _description = 'Get hash integrity result as PDF.'

    @api.model
    def _get_report_values(self, docids, data=None):
        SaleBlanketOrder = self.env['sale.blanket.order']
        order_id = SaleBlanketOrder.browse(docids)
        linked_product_lines_dict = order_id.get_linked_report_data()

        return {
            'doc_ids': docids,
            'doc_model': self.env['sale.blanket.order'],
            'data': data,
            'docs': order_id,
            'linked_product_lines_dict': linked_product_lines_dict
        }
