# -*- coding: utf-8 -*-
{
    'name': 'Portal Sale Webreport',
    'version': '13.0.1.0.9',
    'summary': """This Module Allows""",
    'category': 'Website',
    'depends': [
        'sale',
        'website_sale',
        'report_xlsx',
        'sales_blanket_order',
        'ld_ecommerce_extension',
        'ld_sap_integration'
    ],
    'data': [
        'views/sale_order_views.xml',
        'report/report_xlsx_views.xml',
        'report/sale_order_report_views.xml',
        'report/sale_order_linked_report_views.xml',
        'report/sale_blanket_order_linked_report_views.xml',
        'report/sale_blanket_order_report_views.xml'
    ],
    'images': [
    ],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
