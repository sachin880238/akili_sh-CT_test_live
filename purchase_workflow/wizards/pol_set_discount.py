# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _


class PolSetDiscount(models.TransientModel):
    _name = "pol.set.discount"
    _description = "Purchase order line Set Discount"

    set_discount = fields.Selection([
        ('discount_based_on_price_list', 'set Discount based on price list'),
        ('discount_to', 'set Discount to')
        ])
    set_discount_line = fields.Float(string='Discount')

    @api.multi
    def set_discount_selected_orderlines(self):
        po_line_ids = self.env['purchase.order.line'].browse(self._context.get('o2m_selection').get('order_line').get('ids'))    
            
        if self.set_discount == 'discount_to':
            for line in po_line_ids:
                line.discount = self.set_discount_line
        if self.set_discount == 'discount_based_on_price_list':
            for line in po_line_ids:
                line._onchange_discount()
