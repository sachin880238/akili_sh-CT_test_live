{
    'name' : 'Pre Shipment',
    'version' : '1.1',
    'summary': 'Stock',
    'sequence': 15,
    'description': """
                Pre Shipment
                   """,
    'category': 'stock',    
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends' : ['sale_management', 'stock', 'web_one2many_checkbox','sale', 'base', 'product_extension'],
    'data': [ 
        'security/ir.model.access.csv',
        'views/pre_shipment_view.xml',
        'views/sale_order_view.xml',
        'wizard/pre_shipment_merge_view.xml',
        'wizard/stock_product_line_view.xml',
    ],  
    'installable': True,
    'application': True,
    'auto_install': False, 
}
