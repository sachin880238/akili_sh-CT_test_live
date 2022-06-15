from odoo import fields, models, _


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    is_moved = fields.Boolean(default=False, string="Is Moved")
    product_tracking = fields.Selection(related="product_id.tracking")