# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _ 
 
class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    pur_desc_id = fields.Many2one('vendor.description', 'Description')

class CustomerDescription(models.Model):
    _name = 'customer.description'
    _description = 'Customer Description'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence')
    name = fields.Char('Name',required=True)
    type = fields.Selection([('contact', 'Contact'), ('delivery', 'Shipping'),
                             ('invoice', 'Billing'), ('account', 'Account')], string='Type', required=True)

class VendorDescription(models.Model):
    _name = 'vendor.description'
    _description = 'Vendor Description'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence')
    name = fields.Char('Name',required=True)
    type = fields.Selection([('contact', 'Contact'),
                             ('purchase', 'Purchasing'), ('invoice', 'Payment'),('delivery','Shipping'),('account', 'Account')], string='Type',required=True)


class PartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    for_vendor = fields.Boolean(string='For Vendors')
    type = fields.Selection([('contact', 'Contact'), ('delivery', 'Shipping'),
                             ('invoice', 'Billing'), ('account', 'Account')], string='Type')
    type_vendor = fields.Selection([('contact', 'Contact'),
                             ('purchase', 'Purchasing'), ('invoice', 'Payment'),('delivery','Shipping'),('account', 'Account'),], string='Type')
    c_parent_id = fields.Many2one('res.partner.category', string="Parent Category")
