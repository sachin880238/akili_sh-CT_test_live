# -*- coding: utf-8 -*-
{
    'name': "Location Address",
    'summary': """Locations For warehouse""",
    'description': """Long description of module's purpose""",
    'author': 'Akili Systems Pvt. Ltd.',
    'website': "http://www.akilisystems.in",
    'category': 'Warehouse',
    'version': '1.0',
    'depends': ['base', 'stock', 'stock_account', 'sale', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/route_rule_type.xml',
        'data/routes_type_data.xml',
        'views/location_view.xml',
        'views/location_route_views.xml',
        'views/operation_types_views.xml',
        'views/route_type_views.xml',
        'views/routes_rules_views.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_rule.xml',
    ],
}
