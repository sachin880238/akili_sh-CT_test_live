{
    'name': 'Custom Base',
    'version': '1.1',
    'category': 'Base',
    'description': """
Customized version of base.
===================================================
""",
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': [
        'base', 
        'hr', 
        'lee_auth',
        'sales_team',
        'purchase',
        'account',
        'stock',
        'project',
        'mrp',
        'point_of_sale',
        'system_app',
        'helpdesk_lite'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets_view.xml',
        'data/res_users_data.xml',
        'views/res_company_views.xml',
        'views/res_users_views.xml',
        'views/teams_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'active': True,
}

