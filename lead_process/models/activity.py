from odoo import api, models, fields, tools, _

class MailActivity(models.Model):
    _inherit = "mail.activity"

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    