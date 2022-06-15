from . import models
from odoo import api, SUPERUSER_ID

# TO REMOVE in master
def uninstall_procurement_jit(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.module.module'].search([
        ('name', '=', 'procurement_jit'),
        ('state', '=', 'installed')
    ]).write({'state': 'uninstalled'})