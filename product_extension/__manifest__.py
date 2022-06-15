# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Product Extension',
    'version' : '1.1',
    'summary': 'Product',
    'sequence': 15,
    'description': """
                 Partner and varient Design and flow change
                   """,
    'category': 'Product',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['product','sale','account','delivery','account','product_team',
                 'point_of_sale','stock_account','website_sale',
                 'sale_management','sale_purchase','product_expiry','mrp','shipping_estimator',
                 'sale_crm','stock','stock_dropshipping', 'vendor_product'],
    'data': [ 
        'views/product_varient_view.xml',
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'wizard/generate_prod_varient_wizard_view.xml', 
    ],  
    'qweb': ['static/src/xml/many2many_checkboxes.xml', ],
    'installable': True,
    'application': True,
    'auto_install': False, 
}
