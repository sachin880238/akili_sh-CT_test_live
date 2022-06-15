{
    'name': 'Website Menu',
    'description': '',
    'version': '1.1',
    'category': 'Ecommerce',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': ['website', 'auth_oauth', 'website_sale', 'custom_base', 'base','stock_picking_batch'],
    'data': [
        'data/menu_data.xml',
        'views/assets.xml',
        'views/templates.xml',
        'data/res_users_data.xml',
        'views/website_menu_views.xml',
        'views/res_config_views.xml',
        'views/website_categ_view.xml'
    ],
    'qweb': [
        'static/src/xml/template.xml',
        'static/src/xml/menu.xml',
        'static/src/xml/dynamic_coloum.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'assign_default_arrow_color',
}
