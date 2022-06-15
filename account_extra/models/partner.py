# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError
import time
import logging

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    #Sales tab
    property_delivery_carrier_id = fields.Many2one('delivery.carrier', string="Ship Via", 
                                   company_dependent=True, help="The Shipment Service Provider for the Delivery.")
    
    # Purchase Tab 
    pur_property_delivery_carrier_id = fields.Many2one('delivery.carrier', company_dependent=True, string="Delivery Method", help="This delivery method will be used when invoicing from picking.")


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    _order = 'sequence'
    sequence = fields.Integer(string="Sequence")
    dash_icon = fields.Char(string="icon",default='fas fa-rectangle-portrait')
    refund_icon = fields.Char(string="icon",default='fas fa-dollar-sign')

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_sale_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_sale_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
