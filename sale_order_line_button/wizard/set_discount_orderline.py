# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _


class SetDiscountOrderLine(models.TransientModel):
    _name = "set.discount.orderline"
    _description = "Set Discount Orderline"

    set_discount = fields.Selection([
        ('discount_based_on_price_list', 'set Discount based on price list'),
        ('discount_to', 'set Discount to')
        ])
    set_discount_line = fields.Float(string='Discount')

    @api.multi
    def set_discount_selected_orderlines(self):
        if self._context.get('sale_order_line'):
            sale_order_line_ids = self.env['sale.order.line'].browse(self._context.get('sale_order_line'))
            
            if self.set_discount == 'discount_to':
                for line in sale_order_line_ids:
                    line.discount = self.set_discount_line
            if self.set_discount == 'discount_based_on_price_list':
                for line in sale_order_line_ids:
                    line._onchange_discount()
