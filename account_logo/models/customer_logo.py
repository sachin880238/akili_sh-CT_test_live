from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_customer_logo = fields.Boolean("Apply on Partners", config_parameter='account_logo.customers_icon')
    background_colour = fields.Char('B.G Colour', config_parameter='account_logo.customers_icon_background_color')
    text_colour = fields.Char('Text Colour', config_parameter='account_logo.customers_icon_text_color')

    apply_existing_partner = fields.Boolean('Apply on Existing Partner', config_parameter='account_logo.existing_customers_icon')

    @api.onchange('apply_existing_partner','background_colour','text_colour')
    def get_apply_existing_partner(self):
        ircp_existing_partner = self.env['ir.config_parameter'].search([('key','=','account_logo.existing_customers_icon')])
        ircp_bg_color = self.env['ir.config_parameter'].search([('key','=','account_logo.customers_icon_background_color')])
        ircp_text_color = self.env['ir.config_parameter'].search([('key','=','account_logo.customers_icon_text_color')])
        if self.apply_existing_partner and not ircp_existing_partner:
            ircp_bg_color.write({'value': self.background_colour})
            ircp_text_color.write({'value': self.text_colour})
            partner_ids = self.env['res.partner'].search([])
            for partner in partner_ids:
                if partner.icon_letters:
                    vals = {'icon_letters': str(partner.icon_letters).lower(), 'is_partner': True}
                    partner.write(vals)
        elif self.apply_existing_partner and (self.background_colour != ircp_bg_color.value or self.text_colour != ircp_text_color.value):
            ircp_bg_color.write({'value': self.background_colour})
            ircp_text_color.write({'value': self.text_colour})
            partner_ids = self.env['res.partner'].search([])
            for partner in partner_ids:
                if partner.icon_letters:
                    vals = {'icon_letters': str(partner.icon_letters).lower(), 'is_partner': True}
                    partner.write(vals)
