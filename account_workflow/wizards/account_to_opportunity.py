
from odoo import models, fields, api

class AccountOpportunity(models.TransientModel):
    _name = 'account.opportunity'
    _description = 'Account Opportunity Wizard'

    name = fields.Char(string='Opportunity')
    stage_id = fields.Many2one('crm.stage', string='Opportunity Stage', default=1)
    user_id = fields.Many2one('res.users','sales_person', index=True, default=lambda self: self.env.user)
    team_id = fields.Many2one('crm.team','sale_team', index=True)
    contact_wizard = fields.Many2one('res.partner',string='Contact')
    partner_wizard = fields.Char(string='Account', compute='find_fields_value')
    opportunity_wizard = fields.Char(string="Name")

    @api.onchange('team_id')
    def onchange_team(self):
        for rec in self:
            if rec.team_id:
                rec.user_id = False
            else:
                rec.user_id = False

    @api.depends('user_id')
    def find_fields_value(self):
        partner_name = self.env['res.partner'].search([('id','=',self._context['active_id'])])
        if partner_name:
            self.partner_wizard= partner_name.name
		 
         
 #............. Convert account to opportunity.................
    @api.multi
    def action_create_opportunity(self):
        active_id = self._context.get('active_ids')
        opp_id = self.env['crm.lead']
        partner_id = self.env['res.partner'].browse(active_id[0])

        values = ({
            'contact_name' : self.contact_wizard.name,
            'name' : self.opportunity_wizard,
            'user_id' : self.user_id.id,
            'partner_id' : partner_id.id,
            'team_id' : self.team_id.id,
            'state' : 'done',
            'stage_id' : self.stage_id.id,
            'type':'opportunity',
            })
        account_opp_id = opp_id.create(values)
        return account_opp_id
