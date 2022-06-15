from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_lead_logo = fields.Boolean("Apply on Leads", config_parameter='account_logo.leads_icon')
    lead_background_color = fields.Char('B.G Colour', config_parameter='account_logo.leads_icon_background_color')
    lead_text_color = fields.Char('Text Colour', config_parameter='account_logo.leads_icon_text_color')

    apply_on_existing_lead = fields.Boolean('Apply on Existing Leads',config_parameter='account_logo.existing_leads_icon')

    @api.onchange('apply_on_existing_lead','lead_background_color','lead_text_color')
    def get_apply_on_existing_lead(self):
        ircp_existing_lead = self.env['ir.config_parameter'].search([('key','=','account_logo.existing_leads_icon')])
        ircp_bg_color = self.env['ir.config_parameter'].search([('key','=','account_logo.leads_icon_background_color')])
        ircp_text_color = self.env['ir.config_parameter'].search([('key','=','account_logo.leads_icon_text_color')])
        if self.apply_on_existing_lead and not ircp_existing_lead:
            ircp_bg_color.write({'value': self.lead_background_color})
            ircp_text_color.write({'value': self.lead_text_color})
            lead_ids = self.env['crm.lead'].search([])
            for lead in lead_ids:
                if lead.lead_icon_letters:
                    vals = {'lead_icon_letters': str(lead.lead_icon_letters).lower()}
                    lead.write(vals)
        elif self.apply_on_existing_lead and (self.lead_background_color != ircp_bg_color.value or self.lead_text_color != ircp_text_color.value):
                ircp_bg_color.write({'value': self.lead_background_color})
                ircp_text_color.write({'value': self.lead_text_color})
                lead_ids = self.env['crm.lead'].search([])
                for lead in lead_ids:
                    if lead.lead_icon_letters:
                        vals = {'lead_icon_letters': str(lead.lead_icon_letters).lower()}
                        lead.write(vals)

