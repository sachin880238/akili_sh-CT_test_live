# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Partner Contacts',
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
    'depends': ['base_setup', 'sales_team', 'stock', 'sale', 'crm', 'account', 'so_workflow', 'purchase',
                'shipment', 'communication_type', 'web_widget_color','l10n_us', 'website_partner'],
    'data': [
        'security/hide.xml',
        'views/partner_view.xml',
        'views/address_partner_view.xml',
        'views/template.xml',
        'views/assets.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
