# -*- coding: utf-8 -*-
{
    'name': 'Custom Dashboard',
    'description': '',
    'version': '1.1',
    'sequence' : 1,
    'category': 'Dashboard',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
   
    'data': ['views/assets.xml',
            'views/dashboard.xml',
            'security/ir.model.access.csv',
            'security/menu.xml',
            ],
    'qweb': ['static/src/xml/menu.xml',
            'static/src/xml/filter_custom.xml',
            'static/src/xml/favorite_ions.xml'
            ],
    'category': 'Creative',
  'depends': ['website','website_theme_install', 'sale', 'board','ct_communication'],
}
