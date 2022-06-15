# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError
import time
import logging
from lxml import etree as ElementTree

old   = '<page name="sales_purchases" string="Sales &amp; Purchases">'
page1 = '<page name="sales_purchases" string="SALES">'
page2 = '<page name="sales_purchases" string="PURCHASING">'
page3 = '<page name="sales_purchases" string="SALES & PURCHASE">'

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    #Sales tab
    sale_shipping_terms = fields.Selection([('prepaid', 'Prepaid'), ('collect', 'Collect'), ('free', 'Free')],
                                        default='prepaid' , string='Ship Terms')
    backorder = fields.Selection([('contact before shipping partial','Contact Before Shipping Partial'),
                ('ship partial, contact when restocked','Ship Partial, Contact When Restocked'),
                ('ship partial, ship when restocked','Ship Partial, Ship When Restocked'),
                ('ship partial, cancel backorder', 'Ship Partial, Cancel Backorder'),('cancel','Cancel')], string="Backorders", 
                default='contact before shipping partial')

    date_last_used = fields.Datetime('Date Created', default=fields.Datetime.now)
    campaign_id = fields.Char(string='Campaign')
    source_id = fields.Char(string='Source')
    medium_id = fields.Char(string='Medium')
    referred = fields.Char(string='Referred By')

    # Purchase Tab
    pur_date_created = fields.Datetime('Date Created', default=fields.Datetime.now)
    vendor_ref = fields.Char(string="Vendor ID")
    ref_customer = fields.Char(string="Customer ID")
    ref_company = fields.Char(string="Company ID")
    products_purchased = fields.Char(string="Products Purchased")
    product_category_id = fields.Many2many('product.category',string="Product Categories")
    vendor_barcode = fields.Char(string="Vendor Barcode")    
    min_order = fields.Monetary(string="Min Order",
                                help="The total amount of the purchase order for this vendor should be above this amount.")
    pur_shipping_terms = fields.Selection([('FOB destination', 'FOB destination'), ('FOB destination, prepay and add', 'FOB destination, prepay and add'),('FOB destination, freight collect','FOB destination, freight collect'),('FOB origin, prepay and allow','FOB origin, prepay and allow'),('FOB origin, prepay and add','FOB origin, prepay and add'),('FOB origin', 'FOB origin')],string='Shipping Terms')
    free_freight = fields.Monetary(
        string='Free Freight Minimum',
        help='Minimum amount to get free Freight'
    ) 
    backorder = fields.Selection([('contact before shipping partial','Contact Before Shipping Partial'),
                ('ship partial, contact when restocked','Ship Partial, Contact When Restocked'),
                ('ship partial, ship when restocked','Ship Partial, Ship When Restocked'),
                ('ship partial, cancel backorder', 'Ship Partial, Cancel Backorder'),('cancel','Cancel')], string="Backorders", 
                default='contact before shipping partial')
    purchase_notes = fields.Text('Purchase Order Notes')
    add_last_used_date = fields.Datetime('Last Used', default=fields.Datetime.now)
    old_account_id = fields.Char('Old Account ID')
    old_address_id = fields.Char('Old Address ID')
       
    @api.onchange('purchase_warn_msg')
    def onchange_purchase_warn_msg(self):
        if self.purchase_warn_msg:
            self.purchase_warn = 'warning' 
        else :
            self.purchase_warn = 'no-message' 
         


    ################################################## Accounting Sales ####################################################
  
    cust_journal_id = fields.Many2one('account.journal', string='Payment Method', domain=[('type', 'in', ('bank', 'cash'))])
    sal_currency_id=fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    statement = fields.Boolean(string='Statement')
    ref_po = fields.Boolean(string='PO or Reference') 
    cust_acc_notes = fields.Text(string='Accounting Notes') 
    cus_acc_bal = fields.Float(string='Account Balance',readonly=True)
    authorized_cards = fields.Char(string="Authorized Cards")
    last_credit_rev = fields.Date(string='Last Credit Review')
    md_tax_id = fields.Char(string='MD Tax ID')
    # Credit Available is a calculated field Credit Available = Credit Limit + Account Balance 
    credit_avl = fields.Float(string='Credit Available',  compute='get_credit_available')
    net_avl_balance = fields.Float(string='Net Available',  compute='get_net_available_balance')
    quotation_warn_msg = fields.Text(string="Quotation msg warning")
    @api.depends('credit_limit','cus_acc_bal')
    def get_credit_available(self):
        for rec in self:
            rec.credit_avl = rec.credit_limit + rec.cus_acc_bal



    # @api.depends('credit_avl','curr_order')
    def get_net_available_balance(self):
        for rec in self:
            rec.net_avl_balance = rec.credit_avl - rec.curr_order


    
    curr_order = fields.Float(string='Current Orders', compute="get_current_orders")
    cust_overdue = fields.Float(string='Overdue',readonly=True)
    cust_avg_days = fields.Integer(string='Average Pay Days',readonly=True)

    @api.multi
    def get_current_orders(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('partner_id','=',rec.id)])
            total_sale_order_amount = 0.0
            total_invoice_amount = 0.0
            for sale in sale_order:
                total_sale_order_amount += sale.amount_total
                if sale.invoice_ids:
                    for invoice in sale.invoice_ids:
                        total_invoice_amount += invoice.amount_total
            rec.curr_order = total_sale_order_amount - total_invoice_amount    


    @api.onchange('invoice_pay_warn_msg')
    def onchange_invoice_pay_warn_msg(self):
        if self.invoice_pay_warn_msg:
            self.invoice_warn = 'warning'
            self.invoice_warn_msg = self.invoice_pay_warn_msg
        else :
            self.invoice_warn = 'no-message'
            self.invoice_warn_msg = self.invoice_pay_warn_msg
        
    @api.onchange('invoice_warn_msg')
    def onchange_invoice_warn_msg(self):
        if self.invoice_warn_msg:
            self.invoice_warn = 'warning' 
        else:
            self.invoice_warn = 'no-message'  

    cust_acc_notes = fields.Text('Accounting Notes')

    ################################### Accounting Purchase ###############################################

    @api.depends('van_acc_bal','van_credit_limit','unhipped_order')
    def _compute_van_credit_avl(self):
        for rec in self:
            if rec.van_acc_bal:
                rec.van_credit_avl = rec.van_credit_limit-rec.van_acc_bal-rec.unhipped_order

    supp_journal_id = fields.Many2one('account.journal', string='Payment Method', domain=[('type', 'in', ('bank', 'cash'))])
    pur_currency_id=fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    is_rfq = fields.Selection([('optional','Optional'),('requried','Requried')],string="Issue RFQ"  )
    van_acc_bal = fields.Monetary(string='Account Balance')
    van_credit_limit = fields.Monetary(string="Credit Limit")
    van_credit_avl = fields.Monetary(string="Credit Available",compute='_compute_van_credit_avl')
    unhipped_order = fields.Monetary(string='Unshipped Orders')
    draft_order = fields.Float(string='Draft Orders')
    supp_overdue = fields.Monetary(string='Overdue')
    supp_avg_days = fields.Integer(string='Average Pay Days')
    last_pay_days = fields.Integer(string='Last Pay Days')
    invoice_pay_warn_msg = fields.Text(string='Payment Warning')
    # desc = fields.Many2one('customer.description', 'Description')
    vd_tax_id = fields.Selection([('Rental','Consumable'),('consumable','Resale'),('Resale','Rental')],string="Taxable")
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartner, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if res['type'] == 'form':
            xml = ElementTree.fromstring(res['arch'])
            if self._context.get('search_default_customer'):
                res['arch'] = res['arch'].replace(old,page1)
            if self._context.get('default_supplier'):
                res['arch'] = res['arch'].replace(old,page2)  
        return res

    @api.onchange('invoice_pay_warn_msg')
    def onchange_invoice_pay_warn_msg(self):
        if self.invoice_pay_warn_msg:
            self.invoice_warn = 'warning'
            self.invoice_warn_msg = self.invoice_pay_warn_msg
        else :
            self.invoice_warn = 'no-message'
            self.invoice_warn_msg = self.invoice_pay_warn_msg

    supp_acc_notes = fields.Text('Accounting Comments')
     
    @api.model
    def default_get(self, fields_list):
        res = super(ResPartner, self).default_get(fields_list)
        country_selected = self.env[
            'res.country'].search([('code', '=', 'US')])      
        #res['copy_contacts'] = True
        res['sale_shipping_terms'] = 'prepaid'
        res['country_id'] = country_selected.id
        return res
