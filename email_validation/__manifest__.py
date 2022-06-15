{
    'name' : 'Email Validation',
    'version' : '1.0',
    'summary': 'Validate email address',
    'description': """
Email Validation
====================
This module provides validation to email address.
""",
	'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': 'https://www.akilisystems.in',
	'depends':['crm','account_contacts','lead_process'],
    'data':['views/email_validation_view.xml'],
    'category': 'Validation',
    'installable': True,
    'application': True,
    'auto_install': False,
}
