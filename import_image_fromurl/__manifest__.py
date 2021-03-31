{
    'name': 'Import Images From URL / CSV / XLS',
    'version': '1.2',
    'category': 'Tools',
    'author': 'FreelancerApps',
    'depends': ['base', 'sale', 'product'],
    'summary': 'Import Product, Customer, Supplier Images From URL, csv, xls file Import Image URL CSV XLS Import Image URL CSV Import Image URL XLS Import Image CSV URL Import Image CSV XLS Import URL Image CSV Import Image XLS URL Import Image XLS CSV Import URL Image XLS Import URL CSV Image Import URL CSV XLS Import CSV Image URL Import CSV Image XLS Import CSV URL Image Import URL XLS CSV Import URL XLS Image Import CSV URL XLS Image Import URL CSV Import XLS Image URL Import CSV XLS Image Import CSV XLS URL Import XLS Image CSV Import XLS URL Image Import XLS URL CSV Image Import XLS Image Import XLS CSV Image Import XLS CSV URL Image Import CSV XLS Image URL Import XLS URL Image CSV Image URL Import XLS Image URL CSV Import XLS CSV Image URL XLS Import URL Image XLS CSV Image XLS Import URL Image URL Image CSV XLS Import CSV XLS Image CSV URL Import XLS Image XLS Import CSV Image XLS URL Import XLS URL CSV XLS CSV URL Import CSV XLS CSV Import XLS CSV URL XLS CSV Import Image CSV URL XLS URL CSV Image CSV URL Import URL Image CSV XLS Image CSV Import CSV URL XLS URL Import Image Import CSV URL CSV Image CSV Import Image URL CSV Image CSV XLS CSV Import URL CSV Image XLS Image Import URL Image Import CSV Import CSV Import XLS CSV XLS Image XLS URL Image XLS Image URL XLS CSV URL XLS Import Image XLS Image CSV XLS URL XLS CSV Import XLS Image XLS CSV Image Import URL Import URL XLS Image URL CSV XLS CSV XLS Import Image Import CSV XLS Import XLS URL Import URL XLS Import CSV XLS URL CSV XLS Import URL XLS Import Image URL Image CSV URL Import',
    'description': '''
Import Product, Customer, Supplier Images From Direct URL / CSV / XLS File
==========================================================================
Add image url directly into Product, Customer, Supplier and system will be automatically import or download image from that url and set to that object
Add Image URL into csv / xls file and import that file then system will be automatically import or download image from that url and set to that object

Key features:
-------------
* Easy To Use.
* Import images from url for product, customer, supplier.
* Import Via directly adding url, csv file, xls file.
* For csv / xls file you have an option to select mapping field like database id, name, internal reference.
* Supporting Create and Write option. So if you update URL and Edit and Save it read again and set Image.
* Maintains Log, so user can check when file was imported and check error if any.
* Set access right, so specific user will set image though url/csv/xls file.

<Search Keyword for internal user only>
---------------------------------------
Import Image URL CSV XLS Import Image URL CSV Import Image URL XLS Import Image CSV URL Import Image CSV XLS Import URL Image CSV Import Image XLS URL Import Image XLS CSV Import URL Image XLS Import URL CSV Image Import URL CSV XLS Import CSV Image URL Import CSV Image XLS Import CSV URL Image Import URL XLS CSV Import URL XLS Image Import CSV URL XLS Image Import URL CSV Import XLS Image URL Import CSV XLS Image Import CSV XLS URL Import XLS Image CSV Import XLS URL Image Import XLS URL CSV Image Import XLS Image Import XLS CSV Image Import XLS CSV URL Image Import CSV XLS Image URL Import XLS URL Image CSV Image URL Import XLS Image URL CSV Import XLS CSV Image URL XLS Import URL Image XLS CSV Image XLS Import URL Image URL Image CSV XLS Import CSV XLS Image CSV URL Import XLS Image XLS Import CSV Image XLS URL Import XLS URL CSV XLS CSV URL Import CSV XLS CSV Import XLS CSV URL XLS CSV Import Image CSV URL XLS URL CSV Image CSV URL Import URL Image CSV XLS Image CSV Import CSV URL XLS URL Import Image Import CSV URL CSV Image CSV Import Image URL CSV Image CSV XLS CSV Import URL CSV Image XLS Image Import URL Image Import CSV Import CSV Import XLS CSV XLS Image XLS URL Image XLS Image URL XLS CSV URL XLS Import Image XLS Image CSV XLS URL XLS CSV Import XLS Image XLS CSV Image Import URL Import URL XLS Image URL CSV XLS CSV XLS Import Image Import CSV XLS Import XLS URL Import URL XLS Import CSV XLS URL CSV XLS Import URL XLS Import Image URL Image CSV URL Import 
    ''',
    'data': [
        'security/import_image_security.xml',
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/res_partner_view.xml',
        'wizard/upload_url_file_view.xml',
    ],
    'images': ['static/description/import_from_url_banner.png'],
    'price':9.99,
    'currency': 'USD',
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
