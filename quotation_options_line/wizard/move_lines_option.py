# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields, _


class Move_lines_product(models.TransientModel):
    _name = "move.lines.product"
    _description = 'Move Lines Product'

    @api.multi
    def move_orderlines_to_option(self):
        sale_order_line = self.env['sale.order.line']
        if self._context.get('selected_o2m_ids'):
            sale_order_option_ids = self.env['sale.order.option'].browse(self._context.get('selected_o2m_ids'))

            for order_line in sale_order_option_ids:
                vals = {
                    'del_days': order_line.del_days,
                    'hold_qty': order_line.hold_qty,
                    'carrier_id': order_line.carrier_id.id,
                    'availability':order_line.availability,
                    'expected_by': order_line.expected_by,
                    'reserve_qty': order_line.reserve_qty,
                    'is_reserved': order_line.is_reserved,
                    'route_id': order_line.route_id.id,
                    'delivery_date': order_line.delivery_date,
                    'price_unit': order_line.price_unit,
                    'order_id': order_line.order_id.id,
                    'name': order_line.name,
                    'product_id': order_line.product_id.id,
                    'product_uom_qty': order_line.quantity,
                    'product_uom': order_line.uom_id.id,
                    'discount': order_line.discount,
                }
                sale_order_line.create(vals)
                order_line.unlink()
        return True