# -*- coding: utf-8 -*-

{
    'name': 'System Menu Item',
    'summary': 'Display System menu Item',
    'description': """Display System Menu Item""",
    'version': '1.0',
    'category': 'Tools',
    'depends': ['base', 'web', 'backend_menuitem','auth_oauth'],
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'data': [
        'security/help_security.xml',
        'security/ir.model.access.csv',
        'views/system_menu_view.xml',
        'views/report_templates.xml',
        'views/res_currency_view.xml',
        'wizard/help_wizard_view.xml',
        'data/cron.xml',
        'data/res_currency_data.xml',
    ],
    'qweb': [
        'static/src/xml/help.xml',
    ],
    'installable': True,
    'auto_install': False,

}