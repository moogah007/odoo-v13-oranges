{
    'name': 'Website Product Visibility Per Customer Or Guest',
    'version': '1.4.1',
    'category': 'eCommerce',
    'author': 'FreelancerApps',
    'summary': 'hide product per customer, invisible product on web shop per login user, limited product for guest or any user user, website product filter',
    'description': """
Website Product Visibility Per Customer Or Guest
================================================
With the help of this module you can visible / invisible any product, product category per customer or for guest on webshop. 
Administrator have access to set which product will visible for any user or guest user.

Key features:
-------------
* Easy To Use.
* Admin can set which product will visible for logged in user.
* Admin can set which product will visible for guest user.
* Admin can set which product category and all product from that category will visible for logged in user.
* Admin can set which product category and all product from that category will visible for guest user.
* Product can be easily select from Sale Order history.
* Setting is per customer so a product can be visible to one user but not visible to another user.

<Search Keyword for internal user only>
---------------------------------------
Website Product Visibility Visible Website Product Visibility Website Product Visible Website Visibility Product Website Visibility Visible Product Website Visibility Website Visible Product Website Visible Visibility Product Website Visible Product Visibility Website Visibility Product Visible Visibility Website Product Website Visible 
    """,
    'depends': ['base', 'sale_management', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_history_view.xml',
        'views/partner_view.xml',
        'views/public_product_view.xml',
        'views/data_file.xml',
        'views/res_config_view.xml',
    ],
    'images': ['static/description/website_product_visibility_odoo_banner.png'],
    'live_test_url': '',
    'price': 11.99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
