# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'


    del_days = fields.Integer("Days")
    carrier_id = fields.Many2one("delivery.carrier", string='Via')
    client_order_ref = fields.Char(related='order_id.client_order_ref', string='Referance', readonly=True, copy=False, store=True,)
    source = fields.Char(related='order_id.origin', string='Source', readonly=True, copy=False, store=True,)
    availability = fields.Integer(string='Availability')
    expected_by = fields.Datetime(string="Validity Date")
    reserve_qty = fields.Float(string="Reserved")
    is_reserved = fields.Boolean(string='Is Reserved')
    is_bundel_item = fields.Boolean("Is Bundle Item")
    route_id = fields.Many2one('stock.location.route',string='Route')
    delivery_date = fields.Datetime(string='Date')
    option_price_subtotal = fields.Float(string="Subtotal" ,readonly=True)
    option_discount_unit = fields.Float(string="Discount", readonly=True)
    

    @api.multi
    def add_order_line_option(self):
        return True
