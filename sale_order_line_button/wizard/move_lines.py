# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class Move_lines_option(models.TransientModel):
    _name = "move.lines.option"
    _description = "Move Lines Option"
 
    @api.multi
    def move_orderlines_to_option(self):
        sale_order_option = self.env['sale.order.option']
        if self._context.get('select_order_line'):
            sale_order_line_ids = self.env['sale.order.line'].browse(self._context.get('select_order_line'))
            for order_line in sale_order_line_ids:
                if order_line.is_bundel_item or order_line.is_bundle:
                    continue
                vals = {
                    # 'del_days': order_line.del_days,
                    'hold_qty': order_line.hold_qty,
                    'carrier_id': order_line.carrier_id.id,
                    'availability':order_line.availability,
                    'expected_by': order_line.expected_by,
                    'reserve_qty': order_line.reserve_qty,
                    # 'is_reserved': order_line.is_reserved,
                    'route_id': order_line.route_id.id,
                    'delivery_date': order_line.delivery_date,
                    'price_unit': order_line.price_unit,
                    'order_id': order_line.order_id.id,
                    'name': order_line.name,
                    'product_id': order_line.product_id.id,
                    'quantity': order_line.product_uom_qty,
                    'uom_id': order_line.product_uom.id,
                    'discount': order_line.discount,
                }
                sale_order_option.create(vals)
                order_line.unlink()
        return True