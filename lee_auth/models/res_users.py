# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    
    _inherit = "res.users"


    default_password  = fields.Boolean('Sign in with Password', default = True)
    email_otp  = fields.Boolean('Sign in with Email OTP')
    sms_otp  = fields.Boolean('Sign in with SMS OTP')
    email_otp_val = fields.Char('Email OTP')
    sms_otp_val = fields.Char('SMS OTP')
    telephone_number = fields.Char('Telepone Number')
    one_time_password = fields.Char('OTP')
    email_address = fields.Char('Email Address')
    user_question = fields.Char(string='Security Question')
    user_answer = fields.Char(string='Answer')

    # def _default_user_ids(self):
    #     user_ids = self._context.get('active_model') == 'res.users' and self._context.get('active_ids') or []
    #     return [
    #         (0, 0, {'user_id': user.id, 'user_login': user.login})
    #         for user in self.env['res.users'].browse(user_ids)
    #     ]

    # user_ids = fields.One2many('security.user', 'user_id', string='Users', default=_default_user_ids)
    


    @api.model
    def update_password(self,pasword,user_id):
        self._cr.execute('UPDATE res_users SET password=%s WHERE id = %s', (pasword, user_id))
        self._cr.commit()

    # @api.multi
    # def send_otp_to_email(self):

        # enail_address field in res_users
        # code of email otp

    @api.multi
    def send_otp(self):
        self.ensure_one()
        if self.email_otp:
            self.email_otp_val = "test1" # self.send_otp_to_email()
        if self.sms_otp:
            # self.sms_otp_val = "test2"
            mobile_otp_obj = self.env['mobile.otp']
            mobile_otp = mobile_otp_obj.create({'send_to': self.telephone_number,'validity': 10})
            self.sms_otp_val = mobile_otp.name
            # self.send_otp_to_mobile()
        return True 

    # @api.multi
    # def send_otp_to_mobile(self):
    #   mobile_otp_obj = self.env['mobile.otp']
    #   for rec in self:
    #       mobile_otp = mobile_otp_obj.create({'send_to': rec.telephone_number,'validity': 10})
    #       rec.sms_otp_val = mobile_otp.name


# class UserSecurity(models.Model):
#     _name = 'security.user'
    
#     user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
#     user_login = fields.Char(string='User Login', readonly=True)
#     user_question = fields.Char(string='Security Question', readonly=True)
#     user_answer = fields.Char(string='Answer', default='')