from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    active_customer_days = fields.Integer("Active Customer Days",config_parameter='account_workflow.active_customer_days', default=30)
    active_vendor_days = fields.Integer('Active Vendor Days',config_parameter='account_workflow.active_vendor_days',default=30)