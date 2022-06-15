# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Product Team',
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
    'depends' : ['product', 'website_sale', 'crm'],
    'data': [ 
        'security/ir.model.access.csv',
        'views/product_team_view.xml',
        'views/territories.xml'
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
