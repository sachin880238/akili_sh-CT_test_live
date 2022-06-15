{
    'name': "Shipping Estimator",
    'summary': """
        To Estimate the Shipping Cost on the sale order""",
    'version': '10.0.1.0.0',
    'category': 'Uncategorized',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'sale_stock', 'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/precision.xml',
        'wizard/estimate_shipping_view.xml',
        'views/shipping_container_view.xml',
        'views/virtual_package_view.xml',
        'views/res_config_settings_views.xml',
    ],
}
