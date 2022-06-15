# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Product Documents',
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
    'depends' : ['base','product_multi_images'],
    'data': [ 
        'views/product_document_view.xml',
        'security/ir.model.access.csv', 
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
