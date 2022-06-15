# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import date,datetime


class TransferOrderLines(models.Model):
    _name = "transfer.order.lines"
    _description = "Transfer Order Lines"
    _rec_name = 'name'

    transfer_id = fields.Many2one('transfer.order')

    name = fields.Char(string='Name')
    product_id = fields.Many2one('product.product')
    req_qty = fields.Integer(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    route_id = fields.Many2one('stock.location.route', string='Route')
    carrier_id = fields.Many2one('delivery.carrier', string='Via')
    due_date = fields.Datetime(string='Date')
    priority = fields.Selection([(' ', 'Very Low'), ('x', 'Low'), ('xx', 'Normal'), ('xxx', 'High')], string='Priority',index="True")