# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('quaotation_line_bom') and self._context.get('order_line_type') == 'line':
            new_args = [('sale_ok', '=', True), ('product_type', '=', 'product')]
        elif self._context.get('quaotation_line_bom') and self._context.get('order_line_type') == 'set':
            new_args = [('sale_ok', '=', True), ('product_type', '=', 'set')]
        elif self._context.get('quaotation_line_bom') and self._context.get('order_line_type') == 'bundle':
            new_args = [('sale_ok', '=', True), ('product_type', '=', 'bundle')]
        elif self._context.get('is_bundle'):
            new_args = []
            active_id = self._context.get('active_id')
            if active_id:
                sale_order = self.env['sale.order'].browse(active_id)
                orderline = False
                for orderline in sale_order.order_line:
                    if orderline.is_bundle:
                        break;
                if orderline:
                    new_args = [('id', '=', orderline.product_id.id)]
        else:
            new_args = args
        return super(ProductProduct, self).name_search(name=name, args=new_args, operator=operator, limit=limit)
