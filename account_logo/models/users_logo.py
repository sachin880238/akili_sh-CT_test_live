from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_user_logo = fields.Boolean("Apply on Users", config_parameter='account_logo.users_icon')
    user_background_color = fields.Char('B.G Colour', config_parameter='account_logo.users_icon_background_color')
    user_text_color = fields.Char('Text Colour', config_parameter='account_logo.users_icon_text_color')

    apply_existing_user = fields.Boolean('Apply on Existing Users', config_parameter='account_logo.existing_users_icon')

    @api.onchange('apply_existing_user', 'user_background_color', 'user_text_color')
    def get_apply_existing_users(self):
        ircp_existing_user = self.env['ir.config_parameter'].search([('key','=','account_logo.existing_users_icon')])
        ircp_bg_color = self.env['ir.config_parameter'].search([('key','=','account_logo.users_icon_background_color')])
        ircp_text_color = self.env['ir.config_parameter'].search([('key','=','account_logo.users_icon_text_color')])
        if self.apply_existing_user and not ircp_existing_user:
            ircp_bg_color.write({'value': self.user_background_color})
            ircp_text_color.write({'value': self.user_text_color})
            user_ids = self.env['res.users'].search([])
            for user in user_ids:
                if user.icon:
                    vals = {'icon': str(user.icon).lower()}
                    user.write(vals)
        elif self.apply_existing_user and (self.user_background_color != ircp_bg_color.value or self.user_text_color != ircp_text_color.value):
            ircp_bg_color.write({'value': self.user_background_color})
            ircp_text_color.write({'value': self.user_text_color})
            user_ids = self.env['res.users'].search([])
            for user in user_ids:
                if user.icon:
                    vals = {'icon': str(user.icon).lower()}
                    user.write(vals)