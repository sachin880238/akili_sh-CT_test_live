# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _


class PolSetRoute(models.TransientModel):
    _name = "pol.set.route"
    _description = "Purchase order line  Set Route"

    set_route = fields.Selection([
        ('default', 'Set default route for each product'),
        ('route', 'set Route to')
        ])
    route_id = fields.Many2one('stock.location.route',string='Route')
 
    @api.multi
    def set_route_selected_orderlines(self):
        po_line_ids = self.env['purchase.order.line'].browse(self._context.get('o2m_selection').get('order_line').get('ids'))
        if self.set_route == 'route':
            for line in po_line_ids:
                line.route_id = self.route_id
        elif self.set_route == 'default':
            for line in po_line_ids:
                line.route_id = (line.product_id.route_ids and line.product_id.route_ids[0].id) or False