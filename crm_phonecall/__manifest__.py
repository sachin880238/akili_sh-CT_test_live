# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "CRM Phone Calls",
    "version": "12.0.1.6.0",
    "category": "Customer Relationship Management",
    "author": "Akili Systems Pvt. Ltd.",
    "website": "https://akilisystems.in",
    "license": "AGPL-3",
    "depends": [
        'crm','calendar','ct_communication'
    ],
    "data": [
        'security/crm_security.xml',
        'security/ir.model.access.csv',
        'wizard/crm_phonecall_to_phonecall_view.xml',
        'views/crm_phonecall_view.xml',
        'views/res_partner_view.xml',
        'views/crm_lead_view.xml',
        'views/res_config_settings_views.xml',
        'report/crm_phonecall_report_view.xml',
    ],
    'installable': True,
}
