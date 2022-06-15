# -*- coding: utf-8 -*-

{
    'name': 'Design Menu',
    'summary': 'Display Design menu',
    'description': """Display Design menu""",
    'version': '1.0',
    'category': 'Tools',
    'depends':['base'],
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'data': [
        'data/design_settings_data.xml',
        'security/design_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/demo_data.xml',
        'views/account_demo_data.xml',
        'views/all_demo_data.xml',
        'views/comm_demo_data.xml',
        'views/employee_demo_data.xml',
        'views/inventory_demo_data.xml',
        'views/manufacturing_demo_data.xml',
        'views/pos_demo_data.xml',
        'views/purchase_demo_data.xml',
        'views/website_demo_data.xml',
        'views/sale_demo_data.xml',
    ], 
    
    'installable' : True,
    'auto_install' : False,

}
