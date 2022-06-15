{
    'name': "Schedule Activity",
    'summary': """
        To Keep record of task that has been scheduled to be done.""",
    'version': '10.0.1.0.0',
    'category': 'Uncategorized',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'base','calendar'
    ],
    'data': [
        'security/schedule_security.xml',
        'views/schedule_activity.xml',
        'data/res_users_data.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False, 
}
