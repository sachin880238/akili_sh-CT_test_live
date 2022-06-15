# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': "Quotation Options Line",
    'summary': "",
    'version': '',
    'category': 'sale',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': [
        'sale_management','web_one2many_checkbox'
    ],
    'data': [
        'views/quotation_option_line_assests.xml',
        'views/order_line_options_views.xml',
        'views/sale_order_views.xml',
        'views/order_line_options_views.xml',
        'wizard/option_set_views.xml',
        'wizard/move_lines_optionview.xml'
    ],
    'installable': True,
}
