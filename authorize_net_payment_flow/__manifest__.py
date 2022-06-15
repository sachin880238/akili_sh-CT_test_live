# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Authorize .net Payment flow',
    'version' : '1.1',
    'summary': 'Payment',
    'sequence': 15,
    'description': """
                 Authorize .net Payment flow 
                   """,
    'category': 'Payment Invoiceing',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['payment_authorize','custom_web_checkout'],
    'data': [
        'security/ir.model.access.csv',
        'views/add_update_card_view.xml'
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
