# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Default List View',
    'version' : '1.1',
    'summary': 'Other',
    'sequence': 15,
    'description': """
                 Set All Menu Items to List View
                   """,
    'category': 'Product',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['sale','crm','account_contacts','payment','base','product','website_sale'],
    'data': [ 
        'views/menuitem_list_view.xml', 
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
