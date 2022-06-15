# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

class MergeOrderLine(models.TransientModel):
    _name = "merge.order.line"
    _description = "Merge Order Line"

    latest_date = fields.Datetime(string='Date')
    carrier_id = fields.Many2one('delivery.carrier',string='Via')
    route_id = fields.Many2one('stock.location.route',string='Route')


    @api.multi
    def merge_lines(self):
        if self._context.get('o2m_selection'):
            sale_order_line_ids = self.env['sale.order.line'].browse(self._context.get('o2m_selection').get('order_line').get('ids'))
            quantity = 0
            for line in sale_order_line_ids:
                quantity += line.product_uom_qty

            sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
            
            for line in sale_order_line_ids:
                self.env['sale.order.line'].create({
                    'order_id': sale_order.id,
                    'name': line.product_id.full_name,
                    'product_id': line.product_id.id,
                    'name_desc1': line.name_desc1,
                    'product_uom_qty': quantity,
                    'route_id': self.route_id.id,
                    'carrier_id': self.carrier_id.id,
                    'delivery_date': self.latest_date,
                    'price_unit': line.product_id.lst_price,
                    'uom_id' : line.product_id.uom_id.id
                })
                break
            sale_order_line_ids.unlink()


# class DeliveryCarrier(models.Model):
#     _inherit = "delivery.carrier"


    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
        # if self._context.get('quaotation_line_bom') and self._context.get('order_line_type') == 'line':
        #     new_args = [('sale_ok', '=', True), ('product_type', '=', 'product')]
        # elif self._context.get('quaotation_line_bom') and self._context.get('order_line_type') == 'set':
        #     new_args = [('sale_ok', '=', True), ('product_type', '=', 'set')]
        # elif self._context.get('quaotation_line_bom') and self._context.get('order_line_type') == 'bundle':
        #     new_args = [('sale_ok', '=', True), ('product_type', '=', 'bundle')]
        # elif self._context.get('is_bundle'):
        #     new_args = []
        #     active_id = self._context.get('active_id')
        #     if active_id:
        #         sale_order = self.env['sale.order'].browse(active_id)
        #         for orderline in sale_order.order_line:
        #             if orderline.is_bundle:
        #                 break;
        #         new_args = [('id', '=', orderline.product_id.id)]
        # else:
        #     new_args = args
        # return super(ProductProduct, self).name_search(name=name, args=new_args, operator=operator, limit=limit)
