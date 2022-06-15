from odoo import fields, models, api, _



class CrmTeam(models.Model):
    _inherit = 'crm.team'

    team = fields.Selection([
        ('sales_product_team', 'Sales Product Team'),
        ('sales_review_team', 'Sales Review Team'),
        ('purchase_product_team', 'Purchase Product Team'),
        ('warehouse_team', 'Warehouse Team')], string='Type')

    product_category_id = fields.Many2many('product.category',string="Product Categories")

    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('active', 'ACTIVE'),
        ('inactive', 'INACTIVE')],
        default='active', track_visibility='onchange', readonly=True, copy=False)

    @api.multi
    def set_team_state_2_active(self):
        self.write({'state': 'active'})
        return True

    @api.multi
    def set_team_state_2_inactive(self):
        self.write({'state': 'inactive'})
        return True

    @api.multi
    def set_team_state_2_draft(self):
        self.write({'state': 'draft'})
        return True
