{
    'name' : 'Import Utility',
    'version' : '13.0.',
    'summary': 'Partner',  
    'description': """
                 Partner and Contacts View 
                   """,
    'category': 'Sales',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['sales_team', 'base', 'sale'],
    'data': [
        'wizard/wizard_message_view.xml',
        'wizard/import_wizard_views.xml',
        'views/import_data_views.xml',
        'wizard/demo_data.xml',
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
