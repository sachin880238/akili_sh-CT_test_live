{
    'name': 'Employees menuitems',
    'summary': 'Centralize employee menuitems',
    'description': "",
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'version': '1.2',
    'category': 'Human Resources', 
    'license': 'Other proprietary',
    'installable': True,
    'application': True,
    'auto_install': True,
    'depends': [
                'base',
                'hr',
                'hr_timesheet',
                'hr_attendance',
                'hr_holidays',
                ],
    'data': [
            'views/hr_views.xml',
            'data/res_users_data.xml',
            ],
}
