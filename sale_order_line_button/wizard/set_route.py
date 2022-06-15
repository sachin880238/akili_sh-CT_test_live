# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _


class SetRoute(models.TransientModel):
    _name = "set.route"
    _description = "Set Route"

    set_route = fields.Selection([
        ('default', 'Set default route for each product'),
        ('route', 'set Route to')
        ])
    route_id = fields.Many2one('stock.location.route',string='Route')
 
    @api.multi
    def set_route_selected_orderlines(self):
        sale_order_line_ids = self.env['sale.order.line'].browse(self._context.get('sale_order_line'))
        if self.set_route == 'route':
            for line in sale_order_line_ids:
                line.route_id = self.route_id
        elif self.set_route == 'default':
            for line in sale_order_line_ids:
                line.route_id = (line.product_id.route_ids and line.product_id.route_ids[0].id) or False