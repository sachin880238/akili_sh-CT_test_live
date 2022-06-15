{
    'name' : 'Communication Types',
    'version' : '1.0',
    'summary': 'Define communication types',
    'description': """
                 This module gives you a ability to define communication type for your contacts no's. 
                   """,
    'category': 'Communication',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['base','sales_team'],
    'data': [
    		'data/communication_type_data.xml',
            'security/ir.model.access.csv',
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}

