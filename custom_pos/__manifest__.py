{
    'name': 'Custom Pos',
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
        'base', 'point_of_sale',
    ],
    'external_dependencies': {
        'python': [
        ],
    },
    'data': [
        'views/templates.xml',
        'views/pos_order_view.xml',
	

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

    'installable': True
}
