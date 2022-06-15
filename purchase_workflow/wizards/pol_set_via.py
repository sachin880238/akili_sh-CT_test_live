# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _


class polSetVia(models.TransientModel):
    _name = "pol.set.via"
    _description = "Purchase order line Set Via"

    set_via = fields.Selection([
        ('default', 'set default Via for each product '),
        ('via', 'set Via to')])
    carrier_id = fields.Many2one('delivery.carrier',string='Via')

    @api.multi
    def set_via_selected_orderlines(self):
        po_line_ids = self.env['purchase.order.line'].browse(self._context.get('o2m_selection').get('order_line').get('ids'))
        if self.set_via == 'via':
            for line in po_line_ids:
                line.carrier_id = self.carrier_id
        elif self.set_via == 'default':
            for line in po_line_ids:
                line.carrier_id = line.partner_id.pur_property_delivery_carrier_id