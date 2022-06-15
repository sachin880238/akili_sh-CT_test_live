{
    'name': 'Website Protal My Account',
    'version': '1.1',
    'sequence': 1,
    'category': 'Ecommerce',
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'depends': ['website_sale', 'portal', 'helpdesk_lite', 'purchase', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        # =======================================================================
        #       Below views for show menus on user my account page view
        # =======================================================================
        # My Account --> Account Settings
        'views/portal_myhome_templates.xml',
        # My Account --> Address Book
        'views/portal_my_address_templates.xml',
        # My Account --> Customer Service Tickets
        'views/portal_customer_support_tickets.xml',
        # My Account --> Saved Carts
        'views/portal_saved_cart_templates.xml',
        # My Account --> RFQ
        'views/portal_sent_cart_templates.xml',
        # My Account --> Quotation
        'views/portal_quatation_templates.xml',
        # My Account --> Order (SO)
        'views/portal_order_templates.xml',
        # My Account --> Invoices
        'views/portal_invoice_templates.xml',
        # My Account --> Statement
        'views/portal_statement.xml',
        'views/portal_signature.xml',
        'views/portal_purchase_approved.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
