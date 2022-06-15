{
    'name': 'Account Flow',
    'summary': 'Account Flow System',
    'description': """Account Flow System for Customer""",
    'version': '1.0',
    'category': 'Tools',
    'depends': ['base', 'sale', 'account_desc', 'crm', 'lead_process', 'so_workflow'],
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'data': [
        'views/account_flow_view.xml',
        'views/res_config_settings_view.xml',
        'data/auto_deactivate.xml',
        'wizards/account_to_opportunity_wizard.xml',
    ],
    'installable': True,
    'auto_install': True,
}