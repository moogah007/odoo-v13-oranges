# -*- coding: utf-8 -*-
{
    'name': "SIFI Contratos",
    'summary': """SIFI Contratos""",
    'description': """SIFI Contratos""",
    'author': "Moogah",
    'website': "http://www.Moogah.com",
    'category': 'Uncategorized',
    'version': '13.0.1.0.6',
    'depends': [
        'sales_blanket_order',
        'account',
        'ld_sifi',
    ],
    'data': [
        'views/view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'application': True,
}
