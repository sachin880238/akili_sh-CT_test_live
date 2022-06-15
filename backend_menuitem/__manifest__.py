{
    'name': 'Backend Menuitem',
    'version': '1.1',
    'summary': 'Other',
    'sequence': 15,
    'description': """
                 Menuitem backend
                   """,
    'category': 'Product',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': ['sale', 'crm', 'account_contacts', 'so_workflow', 'board', 'sales_team', 'account_voucher','purchase_workflow','ak_dynamic_listview_backend'],
    'data': [
        'views/menuitem_sales_view.xml',
        'views/purchase_menuitem_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}