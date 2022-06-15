from odoo import fields, models, _

class Users(models.Model):
    _inherit = "res.users"

    warehouse_team = fields.Boolean(string="Warehouse Team")
