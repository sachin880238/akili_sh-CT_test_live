# -*- coding: utf-8 -*-
# Copyright 2015-16 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner Credit Hold/Credit Limit',
    'summary': """
        Partner Credit Hold/Credit Limit""",
    'author': "Sodexis, Inc <dev@sodexis.com>",
    'website': 'http://www.sodexis.com',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        'sale',
        'stock',
    ],
    'data': [
        'security/partner_credit_hold_credit_limit_security.xml',
        'security/ir.model.access.csv',
        'wizard/partner_credit_limit_view_warning.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/sale_config_settings_views.xml',
    ],
    'installable': True,
}
