# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class OptionsSet(models.TransientModel):
    _name = "options.set"
    _description = 'Options Set'

    product_id = fields.Many2one('product.product',  string='Product', required=True)

    @api.multi
    def add_set_product_in_options(self):
        sale_option_obj = self.env['sale.order.option'] 

        bom_env = self.env['mrp.bom']
        pro_bom = bom_env.search([('product_id', '=', self.product_id.id),('set_default','=',True)])
        if pro_bom:
            for bom_line in pro_bom.bom_line_ids:
                values = {
                    'order_id': self._context.get('active_id'),
                    'product_id': bom_line.product_id.id,
                    'name': self.product_id.name,
                    'quantity': 1,
                    'price_unit': bom_line.product_id.lst_price,
                    'uom_id' : bom_line.product_id.uom_id.id
                }

                so_option = sale_option_obj.create(values)

        if not pro_bom:
            pro_bom = bom_env.search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),('set_default','=',True)])
            if pro_bom:
                for bom_line in pro_bom.bom_line_ids:
                    values = {}
                    if bom_line.attribute_value_ids:
                        pro_attr = self.product_id.attribute_value_ids.ids
                        bom_attr = bom_line.attribute_value_ids.ids 
                        if list(set(pro_attr).intersection(bom_attr)):
                             values = {
                                 'order_id': self._context.get('active_id'),
                                 'product_id': bom_line.product_id.id,
                                 'name': self.product_id.name,
                                 'quantity': 1,
                                 'price_unit': bom_line.product_id.lst_price,
                                 'uom_id' : bom_line.product_id.uom_id.id
                                } 
                        else:
                            continue  
                    else:
                        values = {
                            'order_id': self._context.get('active_id'),
                            'product_id': bom_line.product_id.id,
                            'name': self.product_id.name,
                            'quantity': 1,
                            'price_unit': bom_line.product_id.lst_price,
                            'uom_id' : bom_line.product_id.uom_id.id
                        }           
                    so_option = sale_option_obj.create(values)
            else:
                raise UserError(_('No BOM found for the Kit.'))
