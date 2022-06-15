from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    carrier_account_ups = fields.Char(related='sale_id.ups_carrier_account', string='Carrier Account', readonly=False)
    service_type_ups = fields.Selection(related='sale_id.ups_service_type', string="Service Type", readonly=False)

