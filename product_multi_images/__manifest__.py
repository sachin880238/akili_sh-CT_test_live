# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Product Multi Images',
    'version' : '1.1',
    'summary': 'Product',
    'sequence': 15,
    'description': """
                 Partner and Multi Images
                   """,
    'category': 'Product',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['product_extension'],
    'data': [ 
        'views/product_template_view.xml',
        'views/product_product_view.xml',
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
