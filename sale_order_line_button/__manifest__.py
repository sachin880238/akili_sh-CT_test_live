# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Sale Order line Button',
    'version' : '1.1',
    'summary': 'Sale',
    'sequence': 15,
    'description': """
                Sale order line Buttons
                   """,
    'category': 'sale',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['sale','web_one2many_checkbox','delivery','base','stock','project'],
    'data': [ 
        'security/ir.model.access.csv',
        'views/sale_order_button_assests.xml',
        'wizard/sale_order_set_bundle_views.xml',
        'wizard/check_stock_views.xml',
        'wizard/set_route_views.xml',
        'wizard/set_via_views.xml',
        'wizard/set_date_orderline_views.xml',
        'wizard/set_discount_orderline_views.xml',
        'wizard/sort_order_line_views.xml',
        'wizard/merge_view.xml',
        'wizard/split_line_view.xml',
        'wizard/move_lines_view.xml',
        'views/sale_order_line_view.xml',
        'views/sale_order_view.xml',
	'views/label.xml',
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
