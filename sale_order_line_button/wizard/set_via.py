# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _


class SaleKitSelection(models.TransientModel):
    _name = "set.via"
    _description = "Set Via"

    set_via = fields.Selection([
        ('default', 'set default Via for each product '),
        ('via', 'set Via to')])
    carrier_id = fields.Many2one('delivery.carrier',string='Via')

    @api.multi
    def set_via_selected_orderlines(self):
        if self._context.get('sale_order_line'):
            sale_order_line_ids = self.env['sale.order.line'].browse(self._context.get('sale_order_line'))
            if self.set_via == 'via':
                for line in sale_order_line_ids:
                    line.carrier_id = self.carrier_id
            elif self.set_via == 'default':
                for line in sale_order_line_ids:
                    line.carrier_id = line.partner_id.property_delivery_carrier_id
