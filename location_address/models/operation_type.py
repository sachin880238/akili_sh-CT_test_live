from odoo import api, fields, models


class OperationType(models.Model):
    _inherit = 'stock.picking.type'

    type_code = fields.Char('Code', required=True)
    stage = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string='Stage', default='draft')
    code = fields.Selection([('incoming', 'delivery'), ('outgoing', 'shipment'), ('internal', 'internal transfer'), ('mrp_operation', 'manufacture'), ('purchase', 'purchase')], 'Process', required=True)
    company_id = fields.Many2one('res.company', 'Company')
    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence', required=False)

    @api.multi
    def name_get(self):
        result = []
        for picking_type in self:
            result.append((picking_type.id, picking_type.name))
        return result

    def activate_operation_type(self):
        self.stage = 'active'

    def inactivate_operation_type(self):
        self.stage = 'inactive'

    def reset_operation_type(self):
        self.stage = 'draft'
