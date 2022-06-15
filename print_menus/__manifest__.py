# -*- coding: utf-8 -*-
{
    'name': "print_menus",
    'version' : '1.1',
    'summary': 'Print Menus',
    'description': """
        Download Report
    """,
    'category': 'Partner Management',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/print_menu_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}