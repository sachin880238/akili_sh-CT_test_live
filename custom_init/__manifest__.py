# -*- coding: utf-8 -*-
{
    'name': 'Custom Init',
    'description': '',
    'version': '1.1',
    'sequence' : 1,
    'category': 'Ecommerce',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': ['website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/website_content_data.xml',
        'data/initialize.xml',
        'data/custom_config_data.xml',
        'views/website_view.xml',
        'views/res_config_views.xml',
        'views/assets.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
