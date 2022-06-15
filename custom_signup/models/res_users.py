# -*- coding: utf-8 -*-
import datetime
import random
from urllib.parse import urljoin
import werkzeug

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    
    _inherit = 'res.users'

    is_email_auth = fields.Boolean("Email Authenticate?", default=False)
    is_password_auth = fields.Boolean("Password Authenticate?", default=True)
    is_mobile_auth = fields.Boolean("Mobile Authenticate?", default=False)
    is_security_auth = fields.Boolean("Security Authenticate?", default=False)
    token_create_time = fields.Datetime("Token Creattime")
    token_valid = fields.Boolean("Token Valid?")
    # login_token_url = fields.Char(compute='_compute_login_token_url', string='Login URL')
    otp = fields.Char("OTP")
    otp_create_time = fields.Datetime("OTP Creattime")
    otp_valid = fields.Boolean("OTP Valid?")
    otp_mobile_no = fields.Char("OTP Mobile No.")
    redirect = fields.Char("Rediret", help="this field is usefull to redirect dynamic link by sign-email.")

    def get_login_url(self, type):
        
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        query = {
            'db': self.env.cr.dbname,
            'token': self.oauth_access_token,
            'id': self.id
        }

        if type == 'signup':
            query.update({'redirect_url': "/my/home"})
            res = urljoin(base_url, "/web/maillogin?%s" % (werkzeug.url_encode(query)))
            return res

        if type == 'get_quote':
            query.update({'redirect_url': "/my/home"})
            res = urljoin(base_url, "/web/maillogin?%s" % (werkzeug.url_encode(query)))
            return res

        if type == 'my_account':
            query.update({'redirect_url': "/my/home"})
            res = urljoin(base_url, "/web/maillogin?%s" % (werkzeug.url_encode(query)))
            return res

        if type == 'redirect':
            query.update({'redirect_url': self.redirect})
            res = urljoin(base_url, "/web/maillogin?%s" % (werkzeug.url_encode(query)))
            return res

        if type == 'without_reset_password':
            token = self.generate_auth_token()
            query.update({
                'redirect_url': "/my/home",
                'token':  token
            })
            res = urljoin(base_url, "/web/maillogin?%s" % (werkzeug.url_encode(query)))
            return res


    def generate_auth_token(self):
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        token =  ''.join(random.SystemRandom().choice(chars) for i in range(20))
        self.oauth_access_token = token
        self.token_create_time = datetime.datetime.now()
        self.token_valid = True
        return token
