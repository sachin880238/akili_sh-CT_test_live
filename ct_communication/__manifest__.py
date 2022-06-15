{
    'name': 'Communication',
    'version': '1.0.',
    'summary': 'Communication',
    'description': """
        Conservation Technology Communication
        """,
    'category': 'Communication',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': ['base', 'sale', 'account_contacts', 'account_workflow'],
    'data': [
        'security/communication_security.xml',
        'security/ir.model.access.csv',
        'views/ct_commu_view.xml',
        'data/res_users_data.xml',
        'views/assets.xml',
        'views/ct_directory_view.xml',
        'wizard/wizard.xml'
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
