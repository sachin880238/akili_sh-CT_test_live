{
    'name': 'Stock Transfer',
    'version': '1.1',
    'category': 'Tool',
    'description': """
Customized version of base.
===================================================
""",
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': ['base','stock','delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_transfer_view.xml',
        'views/stock_transfer_assets_view.xml',
        'data/stock_transfer_data_view.xml',
    ],
    'installable': True,
    'auto_install': True,
    'active': True,
}

