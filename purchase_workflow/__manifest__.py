# -*- coding: utf-8 -*-
# Copyright 2016 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Purchase Order Workflow",
    'summary': "Purchase Order",
    'version': '10.0.1.0.0',
    'category': 'Sale',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'license': 'AGPL-3',
    'installable': True,
    'depends': [ 
        'purchase', 'base', 'account_contacts', 'vendor_product'
    ],
    'data': [
        'views/purchase_order_view_inherit.xml',
        'views/purchase_order_line_view.xml',
        'views/purchase_order_assets.xml',
        'wizards/pol_check_stock_view.xml',
        'wizards/pol_set_bundle_view.xml',
        'wizards/pol_set_route_view.xml',
        'wizards/pol_set_via_view.xml',
        'wizards/pol_set_date_view.xml',
        'wizards/pol_set_discount_view.xml',
        'wizards/pol_sort_lines_view.xml',
        'wizards/pol_merge_view.xml',
        'wizards/pol_split_view.xml',    
    ],
}
