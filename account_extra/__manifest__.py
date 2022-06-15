# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Partner Delivery',
    'version' : '1.1',
    'summary': 'Partner',
    'sequence': 15,
    'description': """
                 Partner and Contacts View 
                   """,
    'category': 'Partner Management',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['delivery','account_sale_purchase_accounting'],
    'data': [ 
        'views/partner_view.xml',
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
