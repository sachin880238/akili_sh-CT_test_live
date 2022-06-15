
from odoo import models, fields, api
class LeadReject(models.TransientModel):
    _name = 'crm.lead.reject'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    lost_reason =fields.Text('Reason', track_visibility='always')
    
    @api.depends('lost_reason')
    def find_match_lead_name(self):
        lead_id = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        contact_name = ''
        if lead_id.contact_name:
            contact_name += lead_id.contact_name
        if lead_id.company_name: 
            contact_name += ', ' + lead_id.company_name      
        if lead_id.street: 
            contact_name += ', ' + lead_id.street
        if lead_id.street2: 
            contact_name += ' ' + lead_id.street2
        if lead_id.city: 
            contact_name += ', ' + lead_id.city
        if lead_id.state_id.name: 
            contact_name += ' ' + lead_id.state_id.name
        if lead_id.zip: 
            contact_name += ' ' + lead_id.zip
        self.found_customer_lead1 = str(contact_name)
        return contact_name

    found_customer_lead1 = fields.Char(compute='find_match_lead_name', string='Lead')

    @api.multi
    def lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        # leads.write({'lost_reason': self.lost_reason})
        for rec in leads:
            rec.write({'state' : 'close'})
        # return leads.action_set_lost()   



        msg1 ='Lost Reason : ' + self.lost_reason
        msg = str(msg1)                           
        leads.message_post(body=msg)