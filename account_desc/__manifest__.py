# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Partner Description',
    'version' : '1.1',
    'summary': 'Partner',
    'sequence': 15,
    'description': """
                 Add feature to put discriotion in Partner and Contacts View 
                   """,
    'category': 'Partner Management',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['sale','purchase','crm','account_contacts', 'account_logo','base', 'communication_type'],
    'data': [ 
        'security/ir.model.access.csv',
        'views/partner_view.xml',
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
