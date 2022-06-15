from odoo import models, fields, api


class StockRule(models.Model):
    _inherit = 'stock.rule'

    stage = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], default='draft')
    description = fields.Char('Description')
    code = fields.Char('Code')

    def activate_stock_rule(self):
        self.stage = 'active'

    def inactivate_stock_rule(self):
        self.stage = 'inactive'

    def reset_stock_rule(self):
        self.stage = 'draft'
