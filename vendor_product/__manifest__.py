{
    'name': 'Vendor Products',
    'version': '1.1',
    'category': 'Purchasing',
    'depends': ['base', 'project', 'account_sale_purchase_accounting'],
    'description': """
    This is the base module for managing vendor products.
    """,
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'data': [
        'security/ir.model.access.csv',
        'views/vendor_product_attribute_views.xml',
        'views/vendor_product_views.xml',
        'views/vendor_product_template_views.xml',
        'views/vendor_product_pricelist_views.xml',
        'views/vendor_product_equivalents_views.xml',
        'views/product_sources_views.xml',
        'wizard/generate_prod_varient_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
