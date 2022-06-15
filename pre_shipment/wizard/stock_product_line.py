
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PreShipmentMerge(models.TransientModel):
    _name = "stock.product.line"
    _description = 'Stock Product Lines'

    latest_date = fields.Date(string='Date')
    carrier_id = fields.Many2one('delivery.carrier',string='Via')
    route_id = fields.Many2one('stock.location.route',string='Route')