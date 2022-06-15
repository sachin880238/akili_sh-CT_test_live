# -*- encoding: utf-8 -*-
{
    "name": "Custom Signup",
    "category": "website",
    'summary': '',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'version': '1.0',
    'description': """
    """,
    "depends": [
         'custom_web_checkout', 'sale', 'auth_oauth', 'custom_init', 'account_contacts', 'mobile_otp', 'communication_type'
    ],
    'data': [
        'data/mail_template_data.xml',
        'data/data.xml',
        'views/auth_signup_templates.xml',
        'views/auth_signin_templates.xml',
        'views/res_users_view.xml', 
        'views/assets.xml',
        'views/checkout_signin_templates.xml',
        'views/auth_oauth_template.xml',
    ],
    'qweb': [
    ],
    "installable": True,
}
