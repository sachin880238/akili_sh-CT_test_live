{
    'name': 'custom chatter',
    'summary': '',
    'version': '1.0',

    'description': """
    """,

    # 'author': '',
    # 'maintainer': '',
    # 'contributors': [''],

    # 'website': '',

    'license': 'AGPL-3',
    'category': 'Uncategorized',

    'depends': [
        'base', 'base_setup', 'bus', 'web_tour','sale'
    ],
    'external_dependencies': {
        'python': [
        ],
    },
    'data': [
        'views/templates.xml',
	

    ],
    'demo': [
    ],
    'js': [
    ],
    'css': [
    ],
    'qweb': [
	'static/src/xml/custom.xml',
    ],
    'images': [
    ],
    'test': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
