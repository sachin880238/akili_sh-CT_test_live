from odoo import api, fields, models, _
from odoo.exceptions import UserError

AVAILABLE_PRIORITIES = [
    (' ', 'Normal'),
    ('x', 'Low'),
    ('x x', 'High'),
    ('x x x', 'Very High'),
]


class Stage(models.Model):
    _inherit = "crm.stage"

    @api.multi
    def unlink(self):
        for stage in self:
            if stage in [stage.env.ref('lead_process.stage_lead_closed'), stage.env.ref('crm.stage_lead1')]:
                raise UserError(_('You cannot delete required stages.'))
        return super(Stage, self).unlink()
    