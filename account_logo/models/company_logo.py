from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_company_logo = fields.Boolean("Apply on Companies", config_parameter='account_logo.company_icon')
    company_background_color = fields.Char('B.G Colour', config_parameter='account_logo.company_icon_background_color')
    company_text_color = fields.Char('Text Colour', config_parameter='account_logo.company_icon_text_color')

    apply_existing_company = fields.Boolean('Apply on Existing Companies', config_parameter='account_logo.existing_company_icon')

    @api.onchange('apply_existing_company', 'company_background_color', 'company_text_color')
    def get_apply_existing_companies(self):
        ircp_existing_company = self.env['ir.config_parameter'].search([('key','=','account_logo.existing_company_icon')])
        ircp_bg_color = self.env['ir.config_parameter'].search([('key','=','account_logo.company_icon_background_color')])
        ircp_text_color = self.env['ir.config_parameter'].search([('key','=','account_logo.company_icon_text_color')])
        if self.apply_existing_company and not ircp_existing_company:
            ircp_bg_color.write({'value': self.company_background_color})
            ircp_text_color.write({'value': self.company_text_color})
            company_ids = self.env['res.company'].search([])
            for company in company_ids:
                if company.icon:
                    vals = {'icon': str(company.icon).lower()}
                    company.write(vals)
        elif self.apply_existing_company and (self.company_background_color != ircp_bg_color.value or self.company_text_color != ircp_text_color.value):
            ircp_bg_color.write({'value': self.company_background_color})
            ircp_text_color.write({'value': self.company_text_color})
            company_ids = self.env['res.company'].search([])
            for company in company_ids:
                if company.icon:
                    vals = {'icon': str(company.icon).lower()}
                    company.write(vals)
