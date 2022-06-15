from odoo import api, fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    purchase_selectable = fields.Boolean("Selectable on Purchase Order Lines")


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['purchase_line_id']
        return fields
