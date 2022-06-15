{
    'name': "Route Purchase",
    'summary': """Enable route functionality on Purchase order lines.""",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in",
    'category': 'Purchases',
    'version': '1.0',
    'depends': ['purchase_stock', 'purchase', 'stock'],
    'data': [
        'security/purchase_stock_security.xml',
        'views/purchase_views.xml',
        'views/stock_views.xml',
        'views/res_config_settings_views.xml',
    ],
}