# -*- encoding: utf-8 -*-
{
    "name": "SIng In Auth",
    "category": "website",
    'summary': '',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'version': '1.0',
    'description': """
    """,
    "depends": [
        'web','custom_web_checkout', 'mobile_otp', 'custom_signup'
    ],
    'data': [
        'views/res_users_view.xml',
        'views/auth_login.xml',
        'views/webclient_templates.xml',
    ],
    "installable": True,
}
