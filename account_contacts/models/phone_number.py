from odoo import api, fields, models
# from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

class Phone(models.Model):
    _name = 'phone.number'
    _description = 'Phone Number'

    name = fields.Char(string='Calling Code')
########################################
# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     @api.one
#     def get_country_code_list(self):
#         country = self.env['res.country'].search([])
#         count_code_list = []
#         for count in country:
#             code = count.phone_code
#             check_dup = ('+'+str(code))
#             exti_phone = self.env['phone.number'].search([('name','=',check_dup)])
#             if not exti_phone:
#                 self.env['phone.number'].sudo().create({
#                             'name':check_dup
#                         })
