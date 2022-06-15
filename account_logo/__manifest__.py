# -*- coding: utf-8 -*-
{
    'name': 'Customer Logo',
    'summary': """This module will add a record to attandance""",
    'version': '1.1',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'category': 'Tools',
    'depends': ['base_setup','base','crm'],
    'data': [
    	'data/logo_data.xml',
        'data/custom_logo_data.xml',
        'views/customer_logo_view.xml',
        'views/res_partner_view.xml',
        'views/users_logo.xml',
        'views/lead_logo_view.xml',
        'views/company_logo.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
