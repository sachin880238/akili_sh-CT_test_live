{
    'name': 'Conservation Custom Backend Web',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'category': 'Partner',
    'version':'1.0',
    'depends': ['web'],
    'description': """
                   This Module Describe the Web Ext
               """,
    'data': [ 
        'views/asset_view.xml',
        'views/webclient_templates.xml'
            ],

    'css': [],
    'qweb': [
        "static/src/xml/*.xml",
            ],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
