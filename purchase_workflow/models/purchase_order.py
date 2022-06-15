from datetime import datetime
from datetime import timedelta 
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import RedirectWarning


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.net_price
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.price_total')
    def _vendor_amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.v_order_line:
                amount_untaxed += line.vendor_prod_net_price
                amount_tax += line.price_tax
            order.update({
                'vendor_amount_untaxed': amount_untaxed,
                'vendor_amount_tax': amount_tax,
                'vendor_amount_total': amount_untaxed + amount_tax,
            })

    v_order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False)
    vendor_amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_vendor_amount_all', track_visibility='always')
    vendor_amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_vendor_amount_all')
    vendor_amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_vendor_amount_all')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_so_line_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_so_line_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    update_price = fields.Boolean(
        string='Update price',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    sub_state1 = fields.Selection([('assign', 'ASSIGN'), ('receive', 'RECEIVE') , ('inspect', 'INSPECT'), ('stock', 'STOCK'), ('invoice', 'INVOICE'), ('closed', 'CLOSED') ],
        default='assign', track_visibility='onchange', readonly=True)
    sub_state2 = fields.Selection([('create', 'DRAFT'),('review', 'REVIEW'), ('revise', 'REVISE'), ('wait', 'WAIT'),('send','SEND'),('confirm','CONFIRM'),('purchase','PURCHASE') ], default='create',
        track_visibility='onchange', readonly=True, copy=False)  
    cancel_state = fields.Char("Last State")
    approved_by=fields.Char(string="Approved By",track_visibility='onchange')
    reason_approve = fields.Char(string="Reason",track_visibility='onchange')
    shipping_terms = fields.Selection([('quoted', 'Quoted'), ('prepaid', 'Prepaid'), ('collect', 'Collect'), ('free', 'Free'),('prepay','add')], default='quoted' , string='Shipping Terms')
    hold_lastval = fields.Float("Approved", track_visibility='onchange' )
    project_count = fields.Integer(string='Opportunities',)
    task_count = fields.Integer(string='Tasks',)
    opp_count = fields.Integer(string='Projects')
    payment_count = fields.Integer(string='Payments')
    card_count = fields.Integer(string='Cards')
    doc_count = fields.Integer(string='Documents')
    order_name = fields.Char(compute="get_order_name")
    priority = fields.Selection([(' ', 'Very Low'), ('x', 'Low'), ('xx', 'Normal'), ('xxx', 'High')], string='Priority',index="True")
    products = fields.Char(related="partner_id.products_purchased", string="Products")
    # For temporarily bases need to change ship_via ship_date and backorder 
    ship_via = fields.Char(string="Ship Via")
    ship_date = fields.Date(string="Ship Date")
    backorders = fields.Selection([('Before_ship', 'Contact Before Shipping Partial'),
                                   ('contact_restocked', 'Ship Partial, Contact When Restocked'),
                                   ('ship_restocked', 'Ship Partial, Ship When Restocked'),
                                   ('cancel_backorders', 'Ship Partial, Cancel Backorder'),
                                   ('cancel_all', 'Cancel All')],
                                   default='Before_ship' , string='Backorders')
    reviewer_id = fields.Many2one('res.users', string='Reviewer', index=True)
    partner_id = fields.Many2one('res.partner', required=True,  change_default=True, track_visibility='always', help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    
    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    dash_icon = fields.Char(string="icon",default='fas fa-rectangle-portrait')

    partner_contact_id = fields.Many2one('res.partner', string='') 
    partner_contact_phone = fields.Text(compute="get_complete_partner_contact_address", string='')
    partner_purchase_id = fields.Many2one('res.partner', string='')
    partner_purchase_address = fields.Text(compute="get_complete_partner_purchase_address", string='')
    partner_invoice_id = fields.Many2one('res.partner', string='')
    partner_invoice_address = fields.Text(compute="get_complete_partner_invoice_address", string='') 
    partner_delivery_id = fields.Many2one('res.partner', string='')
    partner_delivery_address = fields.Text(compute="get_complete_partner_delivery_address", string='')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment term
        - Contact address
        - Purchase address
        - Invoice address
        - Delivery address

        """
        if not self.partner_id:
            self.update({
                'partner_contact_id' : False,
                'partner_purchase_id' : False,
                'partner_invoice_id' : False,
                'partner_delivery_id' : False,

                'partner_contact_phone': False,
                'partner_purchase_address': False,
                'partner_invoice_address' : False,
                'partner_delivery_address' : False,

                'payment_term_id': False,
            })
            return
        if self.partner_id.child_ids:
            addr = {
                'partner_contact_id': False,
                'partner_purchase_id': False,
                'partner_invoice_id': False,
                'partner_delivery_id': False,

                'partner_contact_phone': False,
                'partner_purchase_address': False,
                'partner_invoice_address': False,
                'partner_delivery_address': False,

                'payment_term_id': False,
            }
            # Auto Update default contact addresses in address field in purchase

            for rec in self.partner_id.child_ids:

                if rec.default_address  and rec.vendor_addr_type == 'contact':
                    addr['partner_contact_id'] = rec.id

                    complete_address = ''
                    if rec.name:
                        complete_address += rec.name
                        if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.comp_name: 
                        complete_address += rec.comp_name
                        if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street: 
                        complete_address += rec.street
                        if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street2: 
                        complete_address += rec.street2
                        if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and not rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.zip and not rec.state_id : 
                        complete_address += rec.city + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and rec.zip and not rec.city : 
                        complete_address += rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and not rec.state_id and not rec.zip: 
                        complete_address += rec.city
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and not rec.city and not rec.zip: 
                        complete_address += rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.zip and not rec.city and not rec.state_id: 
                        complete_address += rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if self.company_id:
                        if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                            complete_address += ''
                        else:
                            complete_address += rec.country_id.name

                    addr['partner_contact_phone'] = str(complete_address)

                # Auto Update default Purchase addresses in address field in purchase

                if rec.default_address and rec.vendor_addr_type == 'purchase':
                    addr['partner_purchase_id'] = rec.id

                    complete_address = ''
                    if rec.name:
                        complete_address += rec.name
                        if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.comp_name: 
                        complete_address += rec.comp_name
                        if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street: 
                        complete_address += rec.street
                        if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street2: 
                        complete_address += rec.street2
                        if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and not rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.zip and not rec.state_id : 
                        complete_address += rec.city + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and rec.zip and not rec.city : 
                        complete_address += rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and not rec.state_id and not rec.zip: 
                        complete_address += rec.city
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and not rec.city and not rec.zip: 
                        complete_address += rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.zip and not rec.city and not rec.state_id: 
                        complete_address += rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if self.company_id:
                        if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                            complete_address += ''
                        else:
                            complete_address += rec.country_id.name

                    addr['partner_purchase_address'] = str(complete_address)

                #Auto Update default Billing addresses in address field in purchase
                
                if rec.default_address and rec.vendor_addr_type == 'invoice':
                    addr['partner_invoice_id'] = rec.id

                    complete_address = ''
                    if rec.name:
                        complete_address += rec.name
                        if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.comp_name: 
                        complete_address += rec.comp_name
                        if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street: 
                        complete_address += rec.street
                        if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street2: 
                        complete_address += rec.street2
                        if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and not rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.zip and not rec.state_id : 
                        complete_address += rec.city + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and rec.zip and not rec.city : 
                        complete_address += rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and not rec.state_id and not rec.zip: 
                        complete_address += rec.city
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and not rec.city and not rec.zip: 
                        complete_address += rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.zip and not rec.city and not rec.state_id: 
                        complete_address += rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if self.company_id:
                        if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                            complete_address += ''
                        else:
                            complete_address += rec.country_id.name 

                    addr['partner_invoice_address'] = str(complete_address)

                # Auto Update default Delivery addresses in address field in purchase

                if rec.default_address and rec.vendor_addr_type == 'delivery':
                    addr['partner_delivery_id'] = rec.id

                    complete_address = ''
                    if rec.name:
                        complete_address += rec.name
                        if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.comp_name: 
                        complete_address += rec.comp_name
                        if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street: 
                        complete_address += rec.street
                        if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street2: 
                        complete_address += rec.street2
                        if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and not rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.zip and not rec.state_id : 
                        complete_address += rec.city + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and rec.zip and not rec.city : 
                        complete_address += rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and not rec.state_id and not rec.zip: 
                        complete_address += rec.city
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and not rec.city and not rec.zip: 
                        complete_address += rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.zip and not rec.city and not rec.state_id: 
                        complete_address += rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if self.company_id:
                        if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                            complete_address += ''
                        else:
                            complete_address += rec.country_id.name 

                    addr['partner_delivery_address'] = str(complete_address)

        if self.partner_id.child_ids: 
            values = {
                'payment_term_id': self.partner_id.property_supplier_payment_term_id and self.partner_id.property_supplier_payment_term_id.id or False,
                'partner_contact_id': addr['partner_contact_id'],
                'partner_purchase_id': addr['partner_purchase_id'],
                'partner_invoice_id': addr['partner_invoice_id'],
                'partner_delivery_id': addr['partner_delivery_id'],

                'partner_contact_phone': addr['partner_contact_phone'],
                'partner_purchase_address': addr['partner_purchase_address'],
                'partner_invoice_address': addr['partner_invoice_address'],
                'partner_delivery_address': addr['partner_delivery_address'],
                'user_id': self.partner_id.user_id.id or self.env.uid,
            }
        else:
             values = {
                'partner_contact_id': False,
                'partner_purchase_id': False,
                'partner_invoice_id': False,
                'partner_delivery_id': False,

                'partner_contact_phone': False,
                'partner_purchase_address': False,
                'partner_invoice_address': False,
                'partner_delivery_address': False,
                'user_id': self.partner_id.user_id.id or self.env.uid
            }

        if self.env.user.company_id.sale_note:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.user.company_id.sale_note
        self.update(values)

    @api.multi
    @api.depends('partner_contact_id')
    def get_complete_partner_contact_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])
        if self.partner_contact_id:
            for rec in self.partner_contact_id:
                complete_address = ''
                if rec.name:
                    complete_address += rec.name
                    if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.comp_name: 
                    complete_address += rec.comp_name
                    if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street: 
                    complete_address += rec.street
                    if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street2: 
                    complete_address += rec.street2
                    if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and not rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.zip and not rec.state_id : 
                    complete_address += rec.city + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and rec.zip and not rec.city : 
                    complete_address += rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and not rec.state_id and not rec.zip: 
                    complete_address += rec.city
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and not rec.city and not rec.zip: 
                    complete_address += rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.zip and not rec.city and not rec.state_id: 
                    complete_address += rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if self.company_id:
                    if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                        complete_address += ''
                    else:
                        complete_address += rec.country_id.name
            self.partner_contact_phone = str(complete_address)
        else:
            self.partner_contact_phone = False

    @api.multi
    @api.depends('partner_purchase_id')
    def get_complete_partner_purchase_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])        
        if self.partner_purchase_id:
            for rec in self.partner_purchase_id:
                complete_address = ''
                if rec.name:
                    complete_address += rec.name
                    if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.comp_name: 
                    complete_address += rec.comp_name
                    if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street: 
                    complete_address += rec.street
                    if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street2: 
                    complete_address += rec.street2
                    if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and not rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.zip and not rec.state_id : 
                    complete_address += rec.city + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and rec.zip and not rec.city : 
                    complete_address += rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and not rec.state_id and not rec.zip: 
                    complete_address += rec.city
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and not rec.city and not rec.zip: 
                    complete_address += rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.zip and not rec.city and not rec.state_id: 
                    complete_address += rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if self.company_id:
                    if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                        complete_address += ''
                    else:
                        complete_address += rec.country_id.name
            self.partner_purchase_address = str(complete_address)
        else:
            self.partner_purchase_address = False

    @api.multi
    @api.depends('partner_invoice_id')
    def get_complete_partner_invoice_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])
        if self.partner_invoice_id:
            for rec in self.partner_invoice_id:
                complete_address = ''
                if rec.name:
                    complete_address += rec.name
                    if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.comp_name: 
                    complete_address += rec.comp_name
                    if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street: 
                    complete_address += rec.street
                    if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street2: 
                    complete_address += rec.street2
                    if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and not rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.zip and not rec.state_id : 
                    complete_address += rec.city + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and rec.zip and not rec.city : 
                    complete_address += rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and not rec.state_id and not rec.zip: 
                    complete_address += rec.city
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and not rec.city and not rec.zip: 
                    complete_address += rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.zip and not rec.city and not rec.state_id: 
                    complete_address += rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if self.company_id:
                    if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                        complete_address += ''
                    else:
                        complete_address += rec.country_id.name
            self.partner_invoice_address = str(complete_address)
        else:
            self.partner_invoice_address = False

    @api.multi
    @api.depends('partner_delivery_id')
    def get_complete_partner_delivery_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])
        if self.partner_delivery_id:
            for rec in self.partner_delivery_id:
                complete_address = ''
                if rec.name:
                    complete_address += rec.name
                    if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.comp_name: 
                    complete_address += rec.comp_name
                    if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street: 
                    complete_address += rec.street
                    if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street2: 
                    complete_address += rec.street2
                    if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and not rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.zip and not rec.state_id : 
                    complete_address += rec.city + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and rec.zip and not rec.city : 
                    complete_address += rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and not rec.state_id and not rec.zip: 
                    complete_address += rec.city
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and not rec.city and not rec.zip: 
                    complete_address += rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.zip and not rec.city and not rec.state_id: 
                    complete_address += rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if self.company_id:
                    if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                        complete_address += ''
                    else:
                        complete_address += rec.country_id.name
            self.partner_delivery_address = str(complete_address)
        else:
            self.partner_delivery_address = False

    @api.multi
    def action_po_accept(self):
        self.ensure_one()
        # if self.env.user.id not in self.review_category_id.user_ids.ids:
        #     raise UserError(_('Only members of the Product Team can approve a quotation.'))
        #if self.amount_total >= self.hold_lastval:
        if True:
            self.write({'sub_state2': 'send','lock':True})

    @api.multi
    def action_po_revise(self):
        self.ensure_one()
        # if self.hide_button:
        self.write({
            'sub_state2': 'revise',
        })
        # else:
        #     raise UserError(_('Reviewer does not have access to selected Division'))

    @api.multi
    def action_view_opportunity_1(self):
        if self.opp_count > 0:
            action = self.env.ref('account_workflow.customer_opportunities_tree').read()[0]
            return action
        else:
            tree_view = self.env.ref('lead_process.crm_opportunity_tree_view')
            form_view = self.env.ref('crm.crm_case_form_view_oppor')
            kanban_view = self.env.ref('lead_process.crm_opportunity_kanban_view')
            graph_view = self.env.ref('crm.crm_lead_view_graph')
            pivot_view = self.env.ref('crm.crm_lead_view_pivot')
            calendar_view = self.env.ref('crm.crm_case_calendar_view_leads')
            return {
                'name': _('Opportunities'),
                'view_type': 'form',
                'res_model': 'crm.lead',
                'views': [
                            (tree_view.id,'tree'), (form_view.id,'form'), (kanban_view.id,'kanban'),
                            (graph_view.id,'graph'), (pivot_view.id,'pivot'), (calendar_view.id,'calendar')
                        ],
                'context': {'default_type': 'opportunity','create':False},
                'domain': [('partner_id', '=', self._context.get('active_id', False)),('type','=','opportunity')],
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

    api.multi
    def action_rfq_send(self):
        record = super(PurchaseOrder, self).action_rfq_send()
        if self.sub_state2 == 'review':
            return record
        else :
            self.write({
                'sub_state2': 'confirm',
            })
            return record

    @api.multi
    def button_confirm(self):
        if self.amount_total < self.partner_id.min_order:
            raise UserError(_('Order total value should be greater than or equal to %s')%(self.partner_id.min_order)) 
        if  self.amount_total < self.partner_id.free_freight:
            raise UserError(_('Free freight charges will be applied on the product to avoid it make an order of greater than or equal to %s') %(self.partner_id.free_freight)) 
        if not self.partner_contact_phone:
            raise UserError(_('The Contact is invalid field.'))
        if not self.partner_purchase_address:
            raise UserError(_('The Purchasing is invalid field.'))
        if not self.partner_delivery_address:
            raise UserError(_('The Shipping is invalid field.'))
        
        record = super(PurchaseOrder, self).button_confirm()
        self.write({
            'sub_state2': 'purchase',
            })
        return record
    
    @api.model
    def create(self,vals):
        record = super(PurchaseOrder, self).create(vals)
        if record.partner_id.vendor_state != 'vendor':
            record.partner_id.write({'vendor_state':'vendor'})
        record.partner_id.write({'last_order_date': record.date_order})
        return record

    def get_order_name(self):
        if self.name:
            self.order_name = self.name + ' ' + self.partner_id.name
    @api.multi
    def analyze_order(self):
        return True

    @api.multi
    def action_ready(self):
        self.write({
            'sub_state2': 'review',
        })

    @api.multi
    def button_undone(self):
        return True

    @api.multi
    def action_view_opportunity(self):
        pass

    @api.multi
    def action_view_tasks(self):
        pass

    @api.multi
    def action_view_projects(self):
        pass

    @api.multi
    def action_view_payments(self):
        pass

    @api.multi
    def action_view_cards(self):
        pass

    @api.multi
    def action_view_invoice(self):
        pass

    @api.multi
    def add_stockable_product(self): 
        wizard_form = self.env.ref('purchase_workflow.purchase_order_line_form')
        return {
            'name' : _('Add a Product'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'purchase.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id, 'default_partner_id': self.partner_id.id, 'default_vendor_tab': False}
        }
    
    @api.multi
    def add_vend_stockable_product(self):
        wizard_form = self.env.ref('purchase_workflow.vendor_order_line_form')
        return {
            'name' : _('Add a Vendor Product'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'purchase.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id, 'default_partner_id': self.partner_id.id, 'default_vendor_tab': True}
        }

    @api.multi
    def add_po_line_section(self): 
        wizard_form = self.env.ref('purchase_workflow.purchase_order_line_form')
        return {
            'name' : _('Add Section'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'purchase.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id, 'default_is_section':True}
        } 

    @api.multi
    def add_po_line_note(self): 
        wizard_form = self.env.ref('purchase_workflow.purchase_order_line_form')
        return {
            'name' : _('Add Note'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'purchase.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id, 'default_is_note':True}
        } 

    @api.multi
    def add_po_set_product(self): 
        wizard_form = self.env.ref('purchase_workflow.pol_set_bundle_form_views')
        return {
            'name' : _('Add Product Set'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.set.bundle',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id, 'default_is_set':True}
        }

    @api.multi
    def add_po_bundle_product(self): 
        wizard_form = self.env.ref('purchase_workflow.pol_set_bundle_form_views')
        return {
            'name' : _('Add Product Bundle'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.set.bundle',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id, 'default_is_bundle':True}
        }

    @api.multi
    def remove_bundle_product(self):
        line_obj = self.env['purchase.order.line']
        order_lines = line_obj.search([('order_id','=',self.id),('is_bundle_item','=',True)])
        for line in order_lines:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_delivery_id)
            line.write({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'bundle_id':False,
            })
        order_lines = line_obj.search([('order_id','=',self.id),('is_bundle_item','=',True)])
        order_lines.unlink()
        self.write({'update_price':False})

    @api.multi
    def po_line_check_stock(self):
        if not self.env.context.get('o2m_selection'):
            raise UserError(_('Please Select a Line to Perform this Action.'))

        po_line = self._context.get('o2m_selection').get('order_line').get('ids')
        po_line_ids = self.env['purchase.order.line'].browse(po_line)
        for line in po_line_ids:
            if line.product_id.id == False :
                 raise UserError(_('Please Select the line that has a valid product.'))
            else:
                wizard_form = self.env.ref('purchase_workflow.pol_check_stock_form')
                vals = {
                    'name' : _('Check Stock'),
                    'type' : 'ir.actions.act_window',
                    'res_model' : 'pol.check.stock',
                    'view_id' : wizard_form.id,
                    'view_type' : 'form',
                    'view_mode' : 'form',
                    'target': 'new',
                    'context': {}
                }
        if self.env.context.get('o2m_selection'):
            purchase_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            po_line_ids = self.env['purchase.order.line'].browse(purchase_order_line)
            order_lines = []
            completed_date_list = []
            for line in po_line_ids:
                avl_date = False 
                if line.product_qty <= line.product_id.qty_available:
                    avl_date = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
                #else:
                #    avl_date = self.get_available_date(line.product_id,line.product_uom_qty)
                if avl_date:
                    completed_date_list.append(avl_date)
                #reserver_ids = self.env['reserved.products'].search([('product_id','=',line.product_id.id)])
                incoming_left = 0
                incoming_reserved = 0
                #for reserve in reserver_ids:
                #    incoming_reserved += reserve.waiting  
                incoming_left = line.product_id.incoming_qty -  incoming_reserved  
                val = {
                    'product_id':line.product_id.id,
                    'current_stock':line.product_id.qty_available,
                    'incoming_stock':incoming_left,
                    'requested_qty':line.product_qty,
                    'expected_date' : avl_date
                }
                order_lines.append((0,0,val)) 
            vals['context'].update({
                'data_line' : order_lines,
                'default_data_line' : order_lines,
            })
            if completed_date_list:
                vals['context'].update({
                    'default_completed_date': max(completed_date_list),
                })
        return vals 

    @api.multi
    def po_line_set_route(self):
        purchase_order_line = []
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please Select at least One Order Line to Perform this Action!!!'))
        else:
            purchase_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            po_line_ids = self.env['purchase.order.line'].browse(purchase_order_line)
            for line in po_line_ids:
                if line.product_id.id == False :
                     raise UserError(_('You have selected order line that have invalid product.')) 
        
        wizard_form = self.env.ref('purchase_workflow.pol_set_route_views')
        return {
            'name' : _('Set Route'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.set.route',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }   

    @api.multi
    def po_line_set_via(self):
        purchase_order_line = []
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please Select at least One Order Line to Perform this Action!!!'))
        else:
            purchase_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            po_line_ids = self.env['purchase.order.line'].browse(purchase_order_line)
            for line in po_line_ids:
                if line.product_id.id == False :
                     raise UserError(_('You have selected order line that have invalid product.'))
                      
        wizard_form = self.env.ref('purchase_workflow.pol_set_via_views')
        return {
            'name' : _('Set Via'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.set.via',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }   

    @api.multi
    def po_line_set_date(self):
        purchase_order_line = [] 
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please select at least One Order Line to Perform this Action!!!'))
        
        else:
            purchase_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            po_line_ids = self.env['purchase.order.line'].browse(purchase_order_line)
            for line in po_line_ids:
                if line.product_id.id == False :
                     raise UserError( _('You have selected order lines that have invalid product.')) 
        
        wizard_form = self.env.ref('purchase_workflow.pol_set_date_views')
        return {
            'name' : _('Set Date'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.set.date',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }   

    @api.multi
    def po_line_set_discount(self):
        purchase_order_line = [] 
        if not self._context.get('o2m_selection'):
            raise UserError( _('Please select at least One Order Line to Perform this Action!!!'))
        
        else:
            purchase_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            po_line_ids = self.env['sale.order.line'].browse(sale_order_line)
            for line in po_line_ids:
                if line.product_id.id == False :
                     raise UserError( _('You have selected order lines that have invalid product.'))

        wizard_form = self.env.ref('purchase_workflow.pol_set_discount_views')
        return {
            'name' : _('Set Discount'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.set.discount',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        } 


    @api.multi
    def po_sort_order_lines(self): 
        wizard_form = self.env.ref('purchase_workflow.po_sort_order_lines')
        return {
            'name' : _('Sort Order Lines'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.sort.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }  

    @api.multi
    def po_merge_order_lines(self):
        purchase_order_lines = []
        list_id = []

        if not self._context.get('o2m_selection'):
            raise UserError( _('Please Select two or more than two Lines.')) 

       
        purchase_order_lines = self._context.get('o2m_selection').get('order_line').get('ids')
        po_line_ids = self.env['purchase.order.line'].browse(purchase_order_lines)

        for rec in po_line_ids:
            if rec.product_id.id == False:
                    raise UserError(_('Please Select the line that has a valid product.'))
        
        if len(purchase_order_lines) < 2:
            raise UserError(_('Please Select two or more than two Lines.'))

        for rec in po_line_ids:
            if rec.product_id.id:
                list_id.append(rec.product_id.id)

        for temp in list_id:
            if not  list_id[0]== temp:
                raise UserError(_('Please select those lines whose product is similar.'))

        else:
            latest_date_list = []
            for line in po_line_ids:
                if line.date_planned:
                    latest_date_list.append(line.date_planned)
                else:
                    latest_date_list = False 
        wizard_form = self.env.ref('purchase_workflow.po_merge_line_view')
        return {
            'name' : _('Merge Lines'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.merge',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {    
                        'default_order_id': self.id,
                        'default_latest_date': max(latest_date_list) if latest_date_list else '',
                        'selected_line_route_ids': po_line_ids.mapped('route_id').ids,
                        'selected_line_carrier_ids': po_line_ids.mapped('carrier_id').ids,
                        }
        }  

    @api.multi
    def po_split_order_lines(self):
        purchase_order_line = [] 
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please Select a Line to Perform this Action.'))
        else:
            purchase_order_line = self._context.get('o2m_selection').get('order_line').get('ids')

        if len(purchase_order_line) > 1:
            raise UserError(_('Please select a single line.'))

        po_line_ids = self.env['purchase.order.line'].browse(purchase_order_line)
        for rec in po_line_ids:
            if rec.product_id.id == False:
                raise UserError(_('Please Select the line that has a valid product.'))
            if rec.product_qty <=1 :
                raise UserError(_('Please select a line that has more than 1 quantity'))

        wizard_form = self.env.ref('purchase_workflow.pol_split_line_view')
        return {
            'name' : _('Split Order Lines'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'pol.split',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': { 
                        'default_order_id': self.id,
                        'default_delivery_date': po_line_ids.date_planned,
                        'default_route_id': po_line_ids.route_id.id,
                        'default_carrier_id': po_line_ids.carrier_id.id,
                        'default_product_uom_qty':po_line_ids.product_qty,
                        'select_order_line': purchase_order_line
                        }
        }
