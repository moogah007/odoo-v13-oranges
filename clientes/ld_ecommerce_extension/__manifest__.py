# -*- coding: utf-8 -*-
{
    'name': "ld ecommerce extension",
    'summary': """ld ecommerce extension""",
    'description': """ld ecommerce extension""",
    'author': "Moogah",
    'website': "http://www.Moogah.com",
    'category': 'Uncategorized',
    'version': '13.0.1.1.32',
    'depends': [
        'website_sale',
        'sale',
        'account',
        'ld_sap_integration',
        'website_sale_delivery',
    ],
    'data': [
        'views/view.xml',
        'views/model_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'application': True,
}
