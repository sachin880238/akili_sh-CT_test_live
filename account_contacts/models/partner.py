# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _  
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import logging
from odoo.http import request
from datetime import date,datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'

    pur_desc_id = fields.Many2one('vendor.description', 'Description')
    hide_button = fields.Boolean(compute='is_auto_create_customer_address',store=False, default=False)
    status = fields.Char(compute="get_account_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    @api.depends('parent_state')
    def get_account_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    @api.depends('child_ids')
    def get_icon_color(self):
        for record in self:
            record.quote_icon_color = False
            quotation_id = self.env['sale.order'].search([('partner_id','=',record.id),('quote_stage','in',['draft','review','revise','send','accept','cancel'])])
            for rec in quotation_id:
                if rec.status == '#ed0929':
                    record.quote_icon_color = '1'
                    return True
            for line in quotation_id:
                if line.status == '#f5ee0e':
                    record.quote_icon_color = '2'
                    return True
            for i in quotation_id:
                if i.status == '#0c9f40c9':
                    record.quote_icon_color = '3'
                    return True
            if not record.quote_icon_color:
                record.quote_icon_color = '0'

    quote_icon_color = fields.Char(compute='get_icon_color')


    @api.depends('child_ids')
    def is_auto_create_customer_address(self):
        for rec in self:
            if rec.child_ids:
                rec.hide_button = True

    def auto_create_customer_address(self):
        partner_env=self.env['res.partner']
        count = 4
        for rec in self:
            vals={}
            data_dict = False
            data_dictionary = False
            vals.update({'icon_letters':rec.icon_letters})
            data_dict = {
                    'active':True,
                    
                    'use_acc_comm': True,
                    # 'name':rec.name,
                    # 'comp_name':rec.name,
                    'icon_letters': rec.icon_letters,
                    'street': rec.street,
                    'street2': rec.street2,
                    'street3': rec.street3,
                    'city': rec.city,
                    'state_id': rec.state_id.id,
                    'zip': rec.zip,
                    'country_id': rec.country_id.id,
                    'image': rec.create_image(rec.icon_letters),
                    'email': rec.email,
                    'phone': rec.phone,
                    'primary_tel_type': rec.primary_tel_type.id,
                    'alternate_communication_1': rec.alternate_communication_1,
                    'alternate_commu_type_1': rec.alternate_commu_type_1.id,
                    'alternate_communication_2': rec.alternate_communication_2,
                    'alternate_commu_type_2': rec.alternate_commu_type_2.id,
                    'website': rec.website,
                    'lang': rec.lang
                    }
            vals.update({'name':rec.name})
            if rec.company_type == 'person':
                data_dictionary = {'name': rec.name}
                data_dict.update(data_dictionary)
            
            else:
                data_dictionary = {'comp_name':rec.name}
                data_dict.update(data_dictionary)
            
            if rec.customer:
                for addr_type in range(count):
                    if addr_type == 0:
                        data_dictionary = {'type_extend': 'contact','customer':False,'type':'other'}
                        data_dict.update(data_dictionary)
                        rec.write({'child_ids':[(0,0,data_dict)]})
                        # data=partner_env.create(data_dict)
                    elif addr_type == 1:

                        data_dict1 = {'type_extend': 'invoice','customer':False,'type':'invoice'}
                        data_dict.update(data_dict1)
                        rec.write({'child_ids':[(0,0,data_dict)]})
                        # data=partner_env.create(data_dict)
                    elif addr_type == 2:
                        data_dict2 = {'type_extend': 'delivery','customer':False,'type':'delivery'}
                        data_dict.update(data_dict2)
                        rec.write({'child_ids':[(0,0,data_dict)]})
                        # data=partner_env.create(data_dict)
            if rec.supplier:
                for v_addr_type in range(count):
                    if v_addr_type == 0:
                        data_dictionary1 = {'vendor_addr_type': 'contact','is_supplier':True,'supplier':False,'type':'contact','name':rec.name}
                        data_dict.update(data_dictionary1)
                        rec.write({'child_ids':[(0,0,data_dict)]})
                        if rec.company_type == 'company':
                            update_dict = data_dict.pop('name')
                        # data=partner_env.create(data_dict)
                    elif v_addr_type == 1:
                        data_dict3 = {'vendor_addr_type': 'purchase','is_supplier':True,'supplier':False,'type':'other'}
                        data_dict.update(data_dict3)
                        rec.write({'child_ids':[(0,0,data_dict)]})
                        # data=partner_env.create(data_dict)
                    elif v_addr_type == 2:
                        data_dict4 = {'vendor_addr_type': 'invoice','is_supplier':True,'supplier':False,'type':'invoice'}
                        data_dict.update(data_dict4)
                        rec.write({'child_ids':[(0,0,data_dict)]})
                        # data=partner_env.create(data_dict)
                    elif v_addr_type == 3:
                        data_dict5 = {'vendor_addr_type': 'delivery','is_supplier':True,'supplier':False,'type':'delivery'}
                        data_dict.update(data_dict5)
                        rec.write({'child_ids':[(0,0,data_dict)]})
                        # data=partner_env.create(data_dict)
                    

   
    @api.model
    def custom_get_view_id(self,ids=[]):
        view_id=self.env.ref('account_contacts.custom_address_view_address_res_partner_form')
        return view_id.id

    @api.multi
    def get_comm_attributes(self):
        for rec in self:
            if rec.email:
                rec.get_email = rec.email
            if rec.phone:
                if rec.primary_tel_type:
                    telephone = rec.phone + " ("+ rec.primary_tel_type.name + ")"
                    rec.get_telephone = str(telephone)
                else:
                    rec.get_telephone = rec.phone
            if rec.alternate_communication_1:
                if rec.alternate_commu_type_1:
                    other1 = rec.alternate_communication_1 + " ("+ rec.alternate_commu_type_1.name + ")"
                    rec.get_other1 =  str(other1)
                else:
                    rec.get_other1 =  rec.alternate_communication_1
            if rec.alternate_communication_2:
                if rec.alternate_commu_type_2:
                    other2 =  rec.alternate_communication_2 + " ("+ rec.alternate_commu_type_2.name + ")"
                    rec.get_other2 = str(other2)
                else:
                    rec.get_other2 = rec.alternate_communication_2 
            if rec.website:
                rec.get_website = rec.website
            if not rec.website:
                rec.get_website = ""
            if rec.lang:
                lang = self.env['res.lang'].search([('code','=',rec.lang)]).name
                rec.get_lang = lang

# ...............BUTTONS ON RES PARTNER.........

    @api.multi
    def _action_cart_count(self):
        current_partner_cart_ids = self.env['sale.order'].search([('partner_id','=',self.id),('state','=','draft')])
        self.cart_count = len(current_partner_cart_ids)

    @api.multi
    def _action_quotation_count(self):
        current_partner_quotations_ids = self.env['sale.order'].search([('partner_id','=',self.id),('state','=','sent')])
        self.quotation_count = len(current_partner_quotations_ids)

    @api.multi
    def _action_sale_order_count(self):
        for rec in self:
            current_partner_so_ids = rec.env['sale.order'].search([('partner_id','=',rec.id),('state','=','order')])
            rec.sale_order_count = len(current_partner_so_ids)

    @api.multi
    def _action_order_count(self):
        current_partner_orders_ids = self.env['purchase.order'].search([('partner_id','=',self.id),
                                                                        ('state','in',['sent','draft'])])
        self.order_count = len(current_partner_orders_ids)

    @api.multi
    def _action_purchase_count(self):
        current_partner_purchases_ids = self.env['purchase.order'].search([('partner_id','=',self.id),
                                                                           ('state','=','purchase')])
        self.purchase_count = len(current_partner_purchases_ids)

    @api.multi
    def get_delivery_count(self):
        pass

    desc = fields.Many2one('customer.description', 'Description')
    parent_id = fields.Many2one('res.partner', string='Account')
    name = fields.Char(string="Contact")         
    cart_count = fields.Integer(compute='_action_cart_count',string='Carts')
    quotation_count = fields.Integer(compute='_action_quotation_count',string='Quotations')
    sale_order_count = fields.Integer(compute='_action_sale_order_count', string='Sale Order Count')
    order_count = fields.Integer(compute='_action_order_count',string='Orders')
    purchase_count = fields.Integer(compute='_action_purchase_count',string='Purchase Order Count')
    task_count =fields.Integer(string='Task')
    return_count =fields.Integer(string='Returns')
    shipment_count = fields.Integer(string='Shipments', compute='_compute_shipment_ids')
    delivery_count = fields.Integer(string='Delivery')
    support = fields.Integer(string='Support')
    card_count = fields.Integer(string='Card')
    total_payments = fields.Integer(string='Paymeent')
    current_balance = fields.Integer(string='Balance')
    total_refunds = fields.Integer(string='Refund')
    project_count = fields.Integer(string='Projects')
    documents_count = fields.Integer(string='Documents')
    cust_credit = fields.Integer(string='Credit')
    addr_state = fields.Selection(
        [('active', 'ACTIVE'),
         ('inactive', 'INACTIVE')], default='active', string='State')
    get_default_addr = fields.Selection([('yes','Yes'),('no','No')], string="Default Address")
    get_same_as_account = fields.Selection([('yes','yes'),('no','no')], string="Same as Account", compute="get_address_title")
    company_required = fields.Boolean("Required",compute="_get_company_required")
    state_code = fields.Char(string="State",related="state_id.code")
    complete_address = fields.Text(string="Address", compute="get_complete_address")
    vendor_state = fields.Selection([
        ('prospect', 'PROSPECT'),
        ('vendor', 'VENDOR'),
        ('inactive', 'INACTIVE')], default='prospect')
    vendor_status = fields.Char(string="Status")
    street3 = fields.Char()
    street_address = fields.Char('Address', compute='_compute_street_address')
    account_name = fields.Char(string='Account',compute='get_address_title')
    c_person = fields.Char(string='Person',compute='get_address_title')
    c_company = fields.Char(string='Company',compute='get_address_title')

    @api.depends('street', 'street2', 'street3')
    def _compute_street_address(self):
        for partner in self:
            if all([partner.street, partner.street2, partner.street3]):
                partner.street_address = partner.street + ', ' + partner.street2 + ', ' + partner.street3
            elif all([partner.street, partner.street2]):
                partner.street_address = partner.street + ', ' + partner.street2
            elif all([partner.street, partner.street3]):
                partner.street_address = partner.street + ', ' + partner.street3
            elif all([partner.street2, partner.street3]):
                partner.street_address = partner.street2 + ', ' + partner.street3
            else:
                partner.street_address = partner.street or partner.street2 or partner.street3  or ''

    @api.depends('street','street2','street3','city','state_id','zip','country_id')
    def get_complete_address(self):
        complete_address = ''
        for rec in self:
            if rec.street: 
                complete_address += rec.street
                if any([rec.street2, rec.city, rec.state_id, rec.zip, rec.country_id]):
                    complete_address += '\n'
            if rec.street2: 
                complete_address += rec.street2
                if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.street3: 
                complete_address += rec.street3
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
            if rec.country_id:
                complete_address += rec.country_id.name

            rec.complete_address = str(complete_address)

    @api.depends('name','type_extend','vendor_addr_type')
    def _get_company_required(self):
        for rec in self:
            if rec.name:
                rec.company_required = False
            else:
                rec.company_required = True

    @api.multi
    def _compute_shipment_ids(self):
        for rec in self:
            partner_shipments_ids = rec.env['stock.picking'].search([('partner_id.parent_id','=',rec.id),
                                                                     ('picking_type_id.name','=','Delivery Orders')])
            rec.shipment_count = len(partner_shipments_ids)

    @api.multi
    def get_shipments_view(self):
        '''
        This function returns an action that display existing shipments
        of given partner. It can either be a in a list or in a form
        view, if there is only one shipment to show.
        '''
        action = self.env.ref('shipment.custom_picking_view').read()[0]
        pickings = self.env['stock.picking'].search([('partner_id.parent_id','=',self.id),
                                                     ('picking_type_id.name','=','Delivery Orders')])
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
            return action
        elif pickings:
            form_view = [(self.env.ref('shipment.delivery_order_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
            return action
        else:
            return {
                    'name': _('Shipments'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'view_id': self.env.ref('shipment.delivery_order_tree_view').id,
                    'res_model': 'stock.picking',
                    'domain': [('picking_type_id.name','=','Delivery Orders'),
                               ('partner_id.parent_id','=',self._context.get('active_id', False))],
                    'context':"{'create': False, 'default_is_shipment': True}",
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    }

    @api.multi
    def get_address_title(self):
        for rec in self:
            if rec.name and rec.comp_name:
                name = rec.name + "," + " " + rec.comp_name
            elif rec.comp_name:
                name = rec.comp_name
            elif rec.name:
                name = rec.name
            rec.address_title = name
            if not rec.parent_id:
                rec.get_same_as_account='yes'
                if rec.company_type == 'person':
                    rec.c_person = rec.name
                    rec.c_company = False
                    rec.account_name = rec.name
                else:
                    rec.c_person = False
                    rec.c_company = rec.name
                    rec.parent_id = rec.id
                    rec.account_name = rec.name
            else:
                if rec.use_acc_comm:
                    rec.get_same_as_account='yes'
                else:
                    rec.get_same_as_account='no'

    # @api.onchange('get_default_addr')
    # def default_type(self):
    #     if(self.get_default_addr=='no'):
    #         self.default_address=False
    #     else:
    #         self.default_address=True

    @api.onchange('use_acc_comm')
    def default_acc_comm(self):
        if self.use_acc_comm:
            self.get_same_as_account='yes'
        else:
            self.get_same_as_account='no'

    # @api.onchange('get_same_as_account')
    # def get_default_acc_comm(self):
    #     if(self.get_same_as_account=='no'):
    #         self.use_acc_comm=False
    #     else:
    #         self.use_acc_comm=True

    @api.multi
    def active_partner_address(self):
        self.write({'addr_state': 'active'})  # Active Address
        return True

    @api.multi
    def inactive_partner_address(self):
        self.write({'addr_state': 'inactive'})  # Inactive Address
        return True

    @api.multi
    def get_cart_view(self):
        if self.cart_count > 0:
            action = self.env.ref('account_contacts.customer_carts_list').read()[0]
            return action
        else:
            return {
                    'name': _('Carts'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'view_id': self.env.ref('so_workflow.view_cart_tree').id,
                    'res_model': 'sale.order',
                    'domain':[('partner_id','=',self._context.get('active_id', False)),('state', '=', 'draft')],
                    'context': "{'create':False,'edit':False}",
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    }

    @api.multi
    def get_quotation_view(self):
        action = self.env.ref('account_contacts.customer_quotations_list').read()[0]
        return action

    @api.multi
    def get_so_view(self):
        if self.sale_order_count > 0:
            action = self.env.ref('so_workflow.action_sales_order').read()[0]
            return action
        else:
            return {
                    'name': _('Orders'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'view_id': self.env.ref('sale.view_order_tree').id,
                    'res_model': 'sale.order',
                    'domain':[('partner_id','=',self._context.get('active_id', False))],
                    'search_view_id': self.env.ref('sale.sale_order_view_search_inherit_sale').id,
                    'context':"{'create':False}",
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    }
    @api.multi
    def get_rfq_view(self):
        if self.order_count > 0:
            if self.vendor_state == 'inactive':
                action = self.env.ref('account_contacts.vendor_order_list_view').read()[0]
                return action
        if self.order_count > 0:
            if self.vendor_state != 'inactive':
                action = self.env.ref('account_contacts.vendor_rfq_list').read()[0]
                return action
        if self.vendor_state == 'inactive':
            return {
                'name': _('Orders'),
                'view_type': 'form',
                'view_mode': 'tree,form,kanban',
                'res_model': 'purchase.order',
                'domain': [('partner_id', '=', self._context.get('active_id', False))],
                'context': {'create':False},
                'groups_id': [(4, self.env.ref('purchase.group_purchase_user').id)],
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        if self.vendor_state != 'inactive':
            return {
                'name': _('Orders'),
                'view_type': 'form',
                'view_mode': 'tree,form,kanban',
                'res_model': 'purchase.order',
                'domain': [('partner_id', '=', self._context.get('active_id', False))],
                'groups_id': [(4, self.env.ref('purchase.group_purchase_user').id)],
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

    @api.multi
    def get_purchase_view(self):
        if self.purchase_count > 0:
            action = self.env.ref('account_contacts.vendor_purchase_list').read()[0]
            return action
        else:
            return {
                'name': _('Purchases'),
                'view_type': 'form',
                'view_mode': 'tree,form,kanban',
                'res_model': 'purchase.order',
                'domain': [('partner_id', '=', self._context.get('active_id', False))],
                'groups_id': [(4, self.env.ref('purchase.group_purchase_user').id)],
                'context': "{'create':False}",
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

    @api.multi
    def get_invoice_view(self):
        if self.total_invoiced > 0.0:
            action = self.env.ref('account.action_invoice_refund_out_tree').read()[0]
            action['domain'] = literal_eval(action['domain'])
            action['domain'].append(('partner_id', 'child_of', self.id))
            return action
        else:
            return {
                    'name': _('Invoices'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'view_id': self.env.ref('account.invoice_tree').id,
                    'res_model': 'account.invoice',
                    'domain':[('type','in', ['out_invoice', 'out_refund']), ('state', 'not in', ['draft', 'cancel'])],
                    'search_view_id': self.env.ref('account.view_account_invoice_filter').id,
                    'context':"{'default_type':'out_invoice', 'type':'out_invoice', 'journal_type': 'sale','create':False}",
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    }

    @api.multi
    def action_cust_credit_res_part(self):
        return True
    @api.multi
    def action_task_count_res_part(self):
        return True

    @api.multi
    def action_return_count_res_part(self):
        return True

    @api.multi
    def action_support_res_part(self):
        return True

    @api.multi
    def action_card_count_res_part(self):
        return True

    @api.multi
    def action_current_balance_res_part(self):
        return True

    @api.multi
    def action_total_refunds_res_part(self):
        return True

    @api.multi
    def action_total_payments_res_part(self):
        return True

    @api.multi
    def action_project_count_res_part(self):
        return True

    @api.multi
    def action_documents_count_res_part(self):
        return True


    _order = "sequence"
    sequence = fields.Integer(string='sequence', help="Gives the sequence order when displaying a list of product categories.")

    country_code = fields.Char(related='country_id.code', string='Country Code', readonly=True) 
    primary_telephone = fields.Char(string="Primary Telephone")
    primary_tel_type = fields.Many2one('communication.type', string='Communication Type')
    alternate_communication_1 = fields.Char(string="Alternate Communication 1")
    alternate_commu_type_1 = fields.Many2one('communication.type', string='Communication Type')
    alternate_communication_2 = fields.Char(string="Alternate Communication 2")
    alternate_commu_type_2 = fields.Many2one('communication.type', string='Communication Type')
    street = fields.Char(string="Address")
    
    # fields to display joined Information in non-edit view
    add_date_created = fields.Datetime('Created', default=fields.Datetime.now)
    add_last_used_date = fields.Datetime('Last Used', default=fields.Datetime.now)
    get_email = fields.Char("Email", compute='get_comm_attributes',)
    get_telephone = fields.Char("Telephone", compute='get_comm_attributes',)
    get_other1 = fields.Char("Other", compute='get_comm_attributes',)
    get_other2 = fields.Char("Other", compute='get_comm_attributes',)
    get_website = fields.Char("Website", compute='get_comm_attributes',)
    get_lang = fields.Char("Language", compute='get_comm_attributes',)
    default_address = fields.Boolean('Default')
    child_ids = fields.One2many('res.partner', 'parent_id', string='Address', domain=[('active', '=', True)])
    comp_name = fields.Char(string='Company')
    use_acc_comm = fields.Boolean("Copy Account Communication", dafault=True)
    cus_type = fields.Char('Customer Type')
    icon_letters = fields.Char("Icon", size=2)
    copy_contacts = fields.Boolean("Copy Contacts", default=False)
    current_default = fields.Boolean("Copy Contacts", default=False)
    address_title = fields.Char(string="Address Title", compute='get_address_title')

    type = fields.Selection(
        [('contact', 'contact'),
         ('purchase', 'purchasing'),
         ('invoice', 'billing'),
         ('delivery', 'shipping'),
         ('other', 'other address'),], string='Type',
        help="Used to select automatically the right address according to the context in sales and purchases documents.")
    
    type_extend = fields.Selection(
        [('contact', 'contact'),
         ('invoice', 'billing'),
         ('delivery', 'shipping'),], string='Type', default='contact',
        help="Used to select automatically the right address according to the context in sales documents.")

    @api.onchange('is_supplier')
    def get_is_supplier(self):
        if self.parent_id.supplier:
            self.is_supplier = True
    
    is_supplier = fields.Boolean("Supplier")

    @api.multi
    @api.depends('type_extend', 'vendor_addr_type')
    def get_addr_type(self):
        for rec in self:
            if rec.type_extend and not rec.is_supplier:
                type_dict = dict(self._fields['type_extend'].selection)
                for key,val in type_dict.items():
                    if key == rec.type_extend:
                        if not rec.parent_id:
                            rec.addr_type = 'account'
                        else:
                            rec.addr_type = val
            if rec.vendor_addr_type and rec.is_supplier:
                type_dict = dict(self._fields['vendor_addr_type'].selection)
                for key,val in type_dict.items():
                    if key == rec.vendor_addr_type:
                        if not rec.parent_id:
                            rec.addr_type = 'account'
                        else:
                            rec.addr_type = val

    addr_type = fields.Char('Type', compute=get_addr_type, store=True)

    vendor_addr_type = fields.Selection(
        [('contact', 'contact'),
         ('purchase', 'purchasing'),
         ('invoice', 'payment'),
         ('delivery', 'shipping'),], string='Type', default='contact',
        help="Used to select automatically the right address according to the context in purchase documents.") 


    @api.multi
    def check_address_contrainst(self,address_list, default_line=False):        
        if len(address_list) > 1:
            if default_line in address_list:
                if default_line.default_address:
                    for line in address_list:
                        if line != default_line:
                            line.default_address = False
                else:
                    if all(not line.default_address for line in address_list):
                        for line in address_list:
                            if line != default_line:
                                line.default_address = False
        return {'msg': False}
                    


    @api.onchange('child_ids')
    def onchange_child_ids(self):
        contact_list = []
        billing_list = []
        shipping_list = []
        purchasing_list = []
        default_line = False

        for line in self.child_ids:
            if line.current_default:
                default_line = line
            if line.type_extend == 'contact' and (not line.is_supplier):
                contact_list.append(line)
                continue
            if line.type_extend == 'invoice' and (not line.is_supplier):
                billing_list.append(line)
                continue
            if line.type_extend == 'delivery' and (not line.is_supplier):
                shipping_list.append(line)
                continue

            if line.vendor_addr_type == 'contact' and line.is_supplier:
                contact_list.append(line)
                continue
            if line.vendor_addr_type == 'invoice' and line.is_supplier:
                 billing_list.append(line)
                 continue
            if line.vendor_addr_type == 'delivery' and line.is_supplier:
                shipping_list.append(line)
                continue
            if line.vendor_addr_type == 'purchase' and line.is_supplier:
                purchasing_list.append(line)

        if default_line in contact_list:
            result = self.check_address_contrainst(contact_list,default_line)
            default_line.current_default = False
            # self.current_default = True

        if default_line in shipping_list:            
            result = self.check_address_contrainst(shipping_list,default_line)
            default_line.current_default = False
        
        if default_line in billing_list:
            result = self.check_address_contrainst(billing_list,default_line)
            default_line.current_default = False

        if default_line in purchasing_list:
            result = self.check_address_contrainst(purchasing_list,default_line)
            default_line.current_default = False
        
    @api.onchange('default_address')
    def onchange_default_address(self):
        self.current_default = True
        
    @api.onchange('type_extend', 'vendor_addr_type')
    def onchange_use_acc_comm_type(self):
        if self.type_extend == 'contact' and (not self.is_supplier):
            self.current_default = True
            self.type = 'other'
        if self.type_extend == 'invoice' and (not self.is_supplier):
            self.current_default = True
            self.type = 'invoice'  
        if self.type_extend == 'delivery' and (not self.is_supplier):
            self.current_default = True
            self.type = 'delivery'
        
        if self.vendor_addr_type == 'contact' and self.is_supplier:
            self.current_default = True
            self.type = 'contact'
        if self.vendor_addr_type == 'invoice' and self.is_supplier:
            self.current_default = True
            self.type = 'invoice'  
        if self.vendor_addr_type == 'delivery' and self.is_supplier:
            self.current_default = True
            self.type = 'delivery'
        if self.vendor_addr_type == 'purchase' and self.is_supplier:
            self.current_default = True
            self.type = 'other'
        if self.desc:
            self.desc = False
        if self.pur_desc_id:
            self.pur_desc_id = False
        if self.category_id:
            self.category_id = False

    @api.onchange('use_acc_comm')
    def onchange_use_acc_comm(self):
        # if self.parent_id.company_type == 'person' and self.use_acc_comm:
        #     if not self.name:
        #         self.name = self.parent_id.name
        #         self.comp_name = False
        # if self.parent_id.company_type == 'company' and self.use_acc_comm:
        #     self.name = False
        #     self.comp_name = self.parent_id.name
        if self.parent_id and self.use_acc_comm:
            self.comp_name = self.parent_id.name
            self.email = self.parent_id.email
            self.phone =  self.parent_id.phone
            self.primary_tel_type = self.parent_id.primary_tel_type
            self.mobile = self.parent_id.mobile
            self.primary_telephone = self.parent_id.primary_telephone
            self.alternate_communication_1 = self.parent_id.alternate_communication_1
            self.alternate_commu_type_1 = self.parent_id.alternate_commu_type_1  
            self.alternate_communication_2 = self.parent_id.alternate_communication_2 
            self.alternate_commu_type_2 = self.parent_id.alternate_commu_type_2
            self.website = self.parent_id.website
            self.street = self.parent_id.street 
            self.street2 = self.parent_id.street2
            self.street3 = self.parent_id.street3 
            self.city = self.parent_id.city 
            self.state_id = self.parent_id.state_id.id 
            self.zip = self.parent_id.zip
            self.country_id = self.parent_id.country_id.id
            self.icon_letters = self.parent_id.icon_letters
            # self.image = self.create_image(self.icon_letters)
            self.lang = self.parent_id.lang

    @api.onchange('email', 'phone', 'website', 'primary_tel_type', 'alternate_communication_1', 'alternate_communication_2', 'alternate_commu_type_1', 'alternate_commu_type_2')
    def onchange_comm(self):
        if self.parent_id and self.use_acc_comm:
            if self.email != self.parent_id.email :
                self.use_acc_comm = False
            if self.primary_tel_type != self.parent_id.primary_tel_type :
                self.use_acc_comm = False
            if self.alternate_communication_1 != self.parent_id.alternate_communication_1 :
                self.use_acc_comm = False
            if self.alternate_communication_2 != self.parent_id.alternate_communication_2 :
                self.use_acc_comm = False
            if self.alternate_commu_type_1 != self.parent_id.alternate_commu_type_1 :
                self.use_acc_comm = False
            if self.alternate_commu_type_2 != self.parent_id.alternate_commu_type_2 :
                self.use_acc_comm = False
            if self.phone != self.parent_id.phone :
                self.use_acc_comm = False
            if self.mobile != self.parent_id.mobile :
                self.use_acc_comm = False
            if self.website != self.parent_id.website :
                self.use_acc_comm = False
            if self.comment != self.parent_id.comment :
                self.use_acc_comm = False
        if (self.parent_id.street == self.street and self.parent_id.street2 == self.street2 and self.parent_id.street3 == self.street3 
               and self.parent_id.city == self.city and self.parent_id.zip == self.zip 
               and self.parent_id.state_id == self.state_id and self.parent_id.country_id == self.country_id 
               and (self.parent_id.name == self.comp_name or self.parent_id.company_type == 'person') and self.mobile == self.parent_id.mobile and self.phone == self.parent_id.phone 
           and self.email == self.parent_id.email):
            self.use_acc_comm = True

    @api.onchange('street', 'street2', 'street3', 'city', 'zip', 'state_id', 'country_id', 'comp_name')
    def onchange_address(self):
        if self.parent_id and self.use_acc_comm:
            if self.street != self.parent_id.street:
                self.use_acc_comm = False
            if self.street2 !=  self.parent_id.street2:
                self.use_acc_comm = False
            if self.street3 !=  self.parent_id.street3:
                self.use_acc_comm = False
            if self.city != self.parent_id.city:
                self.use_acc_comm = False
            if self.zip != self.parent_id.zip:
                self.use_acc_comm = False
            if self.country_id != self.parent_id.country_id:
                self.use_acc_comm = False 
            if self.state_id != self.parent_id.state_id:
                self.use_acc_comm = False
            if self.parent_id.company_type == 'company':
                if self.comp_name != self.parent_id.name: 
                    self.use_acc_comm = False
            if self.email != self.parent_id.email: 
                self.use_acc_comm = False

        if (self.parent_id.street == self.street and self.parent_id.street2 == self.street2 and self.parent_id.street3 == self.street3 and self.parent_id.city == self.city and self.parent_id.zip == self.zip 
               and self.parent_id.state_id == self.state_id and self.parent_id.country_id == self.country_id 
               and (self.parent_id.name == self.comp_name or self.parent_id.company_type == 'person') and self.mobile == self.parent_id.mobile and self.phone == self.parent_id.phone 
           and self.email == self.parent_id.email):
                self.use_acc_comm = True
                
            
    # update the cotact Info to the same as account contact
    def change_address(self, vals): 
        if 'street' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'street':vals['street']}) 
        if 'street2' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'street2':vals['street2']})
        if 'street3' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'street3':vals['street3']}) 
        if 'city' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'city':vals['city']}) 
        if 'zip' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'zip':vals['zip']}) 
        if 'state_id' in vals :
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'state_id':vals['state_id']}) 
        if 'country_id' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'country_id':vals['country_id']}) 
        if 'name' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'comp_name':vals['name']})
        if 'phone' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'phone':vals['phone']}) 

        if 'email' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'email':vals['email']}) 

        if 'alternate_communication_1' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'alternate_communication_1':vals['alternate_communication_1']}) 

        if 'alternate_communication_2' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'alternate_communication_2':vals['alternate_communication_2']}) 

        if 'website' in vals:
            for rec in self:
                if not rec.parent_id:
                    same_contact = self.search([('parent_id','=', rec.id),('use_acc_comm','=',True)]) 
                    same_contact.write({'website':vals['website']}) 


    def match_contact_address(self, vals):
        ckeck_list = ['street', 'street2', 'street3', 'city', 'zip', 'state_id', 'country_id']
        check_flag = False
        for val in ckeck_list:
            if val in vals:
                check_flag = True
                break
        if check_flag:   
            same_contact = self.search([('parent_id','=', self.id),('street','=', self.street),
                                        ('street2','=', self.street2), ('street3','=', self.street3), ('city','=', self.city),
                                        ('zip','=', self.zip),('state_id','=', self.state_id.id),
                                        ('country_id','=', self.country_id.id),])  
            same_contact.write({'use_acc_comm':True})

    def match_parent_address(self, vals):
        ckeck_list = ['street', 'street2', 'street3', 'city', 'zip']
        check_flag = False
        for val in ckeck_list:
            if val in vals:
                check_flag = True
                break
        if check_flag:   
            same_contact = self.search([('id','=', self.parent_id.id),('street','=', self.street),
                                        ('street2','=', self.street2), ('street3','=', self.street3),('city','=', self.city),
                                        ('zip','=', self.zip),('state_id','=', self.state_id.id),
                                        ('country_id','=', self.country_id.id),])  
            same_contact.write({'use_acc_comm':True})


    def match_contact_comm(self, vals):
        ckeck_list = ['phone', 'mobile', 'email']
        check_flag = False
        for val in ckeck_list:
            if val in vals:
                check_flag = True
                break
        if check_flag:   
            same_contact = self.search([('parent_id','=', self.id),('phone','=', self.phone),
                                        ('mobile','=', self.mobile),('email','=', self.email),]) 
            same_contact.write({'use_acc_comm':True})

    def strip_string(self, string):
        if string:
            string = string.strip()
            st_list = string.split() 
            if len(st_list) > 1:
                srt = ''
                for i in st_list: 
                    srt = srt + i + ' '
                srt = srt.strip()
                return srt 
            else:
                return string

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.default_address:
                default_id = rec.search([('parent_id', '=',rec.parent_id.id),('default_address','=',True),('type_extend','=',rec.type),('is_supplier','=',False)])
                vendor_default_id = rec.search([('parent_id', '=',rec.parent_id.id),('default_address','=',True),('vendor_addr_type','=',rec.type),('is_supplier','=',True)])
                if len(default_id.ids) >= 1 or len(vendor_default_id.ids) >= 1:
                    raise UserError(_('Please set the another default address of this type or deselect this, than you can remove this address! (Contact: %s, Account: %s)')%(rec.name,rec.parent_id.name))
        return super(ResPartner, self).unlink()

    @api.model
    def default_get(self, fields_list):
        res = super(ResPartner, self).default_get(fields_list)
        country_selected = self.env[
            'res.country'].search([('code', '=', 'US')])
        return res

    
    @api.model
    def create(self, vals):
        if vals.get('default_address',False):
            vals['get_default_addr']='yes'
        if not vals.get('default_address'):
            vals['get_default_addr']='no'
        if vals.get('use_acc_comm',False):
            vals['get_same_as_account']='yes'
        if not vals.get('use_acc_comm'):
            vals['get_same_as_account']='no'
        if 'parent_id' in vals:
            if vals['parent_id']:
                if 'type_extend' in vals:
                    if 'default_address' in vals:
                        if vals['default_address']:
                            default_id = self.search([('parent_id', '=',vals['parent_id']),('default_address','=',True),('type_extend','=',vals['type_extend']),('is_supplier','=',False)]) 
                            if len(default_id.ids):
                                default_id.write({'default_address':False})
                        else:
                            default_id = self.search([('parent_id', '=',vals['parent_id']),('default_address','=',True),('type_extend','=',vals['type_extend']),('is_supplier','=',False)])
                
                if 'vendor_addr_type' in vals:
                    if 'default_address' in vals:
                        if vals['default_address']:
                            vendor_default_id = self.search([('parent_id', '=',self.parent_id.id),('default_address','=',True),('vendor_addr_type','=',vals['vendor_addr_type']),('is_supplier','=',True)]) 
                            if len(vendor_default_id.ids):
                                vendor_default_id.write({'default_address':False})
                        else:
                            vendor_default_id = self.search([('parent_id', '=',self.parent_id.id),('default_address','=',True),('vendor_addr_type','=',vals['vendor_addr_type']),('is_supplier','=',True)])

        res = super(ResPartner, self).create(vals)
        if vals.get('copy_contacts') and vals.get('customer'):
            for i in range(0,3):
                val = {
                  'default_address':False,
                  'use_acc_comm':True,
                  'parent_id':res.id,
                  'name':vals.get('name'),
                  'copy_contacts':False,
                  'customer':False,
                  'email': vals.get('email'),
                  'phone':vals.get('phone'),
                  'primary_tel_type' : vals.get('primary_tel_type'),
                  'alternate_communication_1' : vals.get('alternate_communication_1'),
                  'alternate_communication_2' : vals.get('alternate_communication_2'),
                  'alternate_commu_type_1' : vals.get('alternate_commu_type_1'),
                  'alternate_commu_type_2' : vals.get('alternate_commu_type_2'), 
                  'website' : vals.get('website'),  
                  'comment' : vals.get('comment'),              
                    }
                if i == 0:
                    val['type_extend'] = 'contact'
                    val['type'] = 'other'
                if i == 1:
                    val['type_extend'] = 'invoice'
                    val['type'] = 'invoice'
                if i == 2:
                    val['type_extend'] = 'delivery'
                    val['type'] = 'delivery'
                ct_id = self.create(val)
                ct_id.onchange_use_acc_comm()
            return res

        if vals.get('copy_contacts') and vals.get('supplier'):
            for i in range(0,4):
                val = {
                  'default_address':False,
                  'use_acc_comm':True,
                  'parent_id':res.id,
                  'name':vals.get('name'),
                  'copy_contacts':False,
                  'supplier':False,
                  'email': vals.get('email'),
                  'phone':vals.get('phone'),
                  'primary_tel_type' : vals.get('primary_tel_type'),
                  'alternate_communication_1' : vals.get('alternate_communication_1'),
                  'alternate_communication_2' : vals.get('alternate_communication_2'),
                  'alternate_commu_type_1' : vals.get('alternate_commu_type_1'),
                  'alternate_commu_type_2' : vals.get('alternate_commu_type_2'), 
                  'website' : vals.get('website'),
                  'comment' : vals.get('comment'),              
                    }
                if i == 0:
                    val['vendor_addr_type'] = 'contact'
                    val['type'] = 'other'
                if i == 1:
                    val['vendor_addr_type'] = 'invoice'
                    val['type'] = 'invoice'
                if i == 2:
                    val['vendor_addr_type'] = 'delivery'
                    val['type'] = 'delivery'
                if i == 3:
                    val['vendor_addr_type'] = 'purchase'
                    val['type'] = 'purchase'
                ct_id = self.create(val)
                ct_id.onchange_use_acc_comm()
            return res
        return res
 
    
    @api.one
    def write(self, vals):
        if 'default_address' in vals:
            if vals['default_address']:
                vals['get_default_addr']='yes'
            else:
                vals['get_default_addr']='no'
        if 'street' in vals:
            vals['street'] = self.strip_string(vals['street'])
        if 'street2' in vals:
            vals['street2'] = self.strip_string(vals['street2'])
        if 'street3' in vals:
            vals['street3'] = self.strip_string(vals['street3'])
        if 'city' in vals:
            vals['city'] = self.strip_string(vals['city'])    
        res = super(ResPartner, self).write(vals)       
        if 'default_address' in vals.keys():   
            if vals.get('default_address'): 
                default_id = self.search([('parent_id', '=',self.parent_id.id),('default_address','=',True),('type_extend','=',self.type),('id','!=',self.id),('is_supplier','=',False)])
                vendor_default_id = self.search([('parent_id', '=',self.parent_id.id),('default_address','=',True),('vendor_addr_type','=',self.type),('id','!=',self.id),('is_supplier','=',True)])
                default_id.write({'default_address':False})
                vendor_default_id.write({'default_address':False})
        
        for rec in self:
            if not rec.parent_id:
                rec.change_address(vals)
                rec.match_contact_address(vals)
                rec.match_contact_comm(vals)
            else:
                rec.match_parent_address(vals)               
        return res

class Followers(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].search([('res_model', '=',vals.get('res_model')), ('res_id', '=', vals.get('res_id')), ('partner_id', '=', vals.get('partner_id'))])
            
            if len(dups):
                for p in dups:
                    p.unlink()
        res = super(Followers, self).create(vals)
        return res
