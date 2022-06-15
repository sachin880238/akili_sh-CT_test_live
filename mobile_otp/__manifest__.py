{
    'name': 'Mobile OTP',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'category': 'Partner',
    'version':'1.1',
    'depends': ['custom_web_checkout'],
    'description': """
                   This Module is to generate OTP for mobile authentication
               """,
    'data': [
        'data/email_template.xml',
        'view/mobile_otp_view.xml',
        'security/ir.model.access.csv',
    ],

    'installabele': True,
    'auto_install': False,

}
