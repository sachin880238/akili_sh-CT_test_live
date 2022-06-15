# -*- coding: utf-8 -*-
# Copyright 2016 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "MRP Custom",
    'summary': "mrp",
    'version': '10.0.1.0.0',
    'category': 'Mrp',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'license': 'AGPL-3',
    'installable': True,
    'depends': ['mrp'],
    "qweb":[],
    'data': [
        'views/mrp_view.xml',
        'security/ir.model.access.csv',
    ],
}
