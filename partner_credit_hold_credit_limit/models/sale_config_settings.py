from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    def _get_add_prepayment_test(self):
        return safe_eval(self.env['ir.config_parameter'].sudo().get_param('prepayment_test', 'False'))

    @api.multi
    def set_add_prepayment_test(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'prepayment_test', str(self.add_prepayment_test))

    add_prepayment_test = fields.Boolean(
        default=_get_add_prepayment_test,
        string="Add Prepayment Test",
        help="If selected then the test should be done even if the credit limit is zero."
    )

    @api.multi
    def _get_over_credit_limit(self):
        return safe_eval(self.env['ir.config_parameter'].sudo().get_param('over_credit_limit', 'False'))

    @api.multi
    def set_over_credit_limit(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'over_credit_limit', str(self.add_prepayment_test))

    over_credit_limit = fields.Boolean(
        default=_get_over_credit_limit,
        string="Over Credit Limit Warning",
        help="If selected then the test should be done for over credit."
    )
