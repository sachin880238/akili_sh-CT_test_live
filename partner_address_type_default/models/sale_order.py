# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOSC, Pedro M. Baeza, Sodexis, OdooMRP team
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    dash_cart_icon = fields.Char(string="icon",default='fas fa-shopping-cart')
    dash_quot_icon = fields.Char(string="icon",default='fas fa-rectangle-portrait')
    dash_sale_icon = fields.Char(string="icon",default='fas fa-rectangle-portrait')
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        result = super(SaleOrder, self).onchange_partner_id()
        for line in self.partner_id.child_ids:
            if line.type == 'invoice' and line.default_address:
                self.partner_invoice_id = line.id
            if line.type == 'delivery' and line.default_address:
                self.partner_shipping_id = line.id
        return result
