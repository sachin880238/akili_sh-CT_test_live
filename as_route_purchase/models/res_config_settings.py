from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_route_po_lines = fields.Boolean("Order-Specific Routes", implied_group='as_route_purchase.group_route_po_lines')
