{
    "name": "WEB CHECKOUT CART",
    "category": "website",
    'summary': '',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'version': '1.0',
    'description': """
    """,
    "depends": [
        'website_sale', 'stock', 'sale_order_line_button', 'pre_shipment', 'product_team', 'custom_init'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/mail_template_data.xml',
        'views/assets.xml',
        'views/cart_templates.xml',
        'views/email_exists_templates.xml',
        'views/checkout_template.xml',
        'views/address_template.xml',
        'views/extre_info_view.xml',
        'views/review_confirm_page.xml',
        # 'views/saved_cart_views.xml',
        'views/quotation_portal_template.xml',
    ],
    'qweb': [
    ],
    "installable": True,
}
