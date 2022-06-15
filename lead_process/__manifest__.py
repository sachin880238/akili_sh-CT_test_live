{
    'name': 'Lead Extension',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'category': 'CRM',
    'version':'1.0',
    'depends': ['crm','account_contacts','sale_crm','backend_menuitem', 'communication_type'],
    'description': """
                   
               """,
    'data': [            
            'data/crm_stage_data.xml',
            'wizards/crm_lead_to_opportunity_view.xml',
            'views/crm_lead_view.xml',
            'views/activity.xml',
            'views/lead_opp.xml',
            'views/assets_view.xml',
            'wizards/crm_lead_reject.xml',
            ],

    'installabele': True,
    'auto_install': False,

}
