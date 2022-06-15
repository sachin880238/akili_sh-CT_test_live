# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


class Lee_auth_login(WebsiteSale):
   
    
    @http.route(['/check-existing-email'], type='http', auth="public", methods=['POST'], website=True)
    def check_existing_email(self, **post):
        vals = {}
        if post.get('email'):
            user = request.env['res.users'].sudo().search([('login', '=', post.get('email'))], limit=1)
            if user:
                # user.send_otp()
                if not user.default_password and user.email_otp and not user.sms_otp:
                    vals.update({
                        'login': post.get('email'),
                        'is_open' : 'email'
                    })

                    # logic for update pwd in query 
                    user.update_password(user.email_otp_val,user.id)
                    return request.render('web.login', vals)

                if not user.default_password and not user.email_otp and  user.sms_otp:
                    vals.update({
                        'login': post.get('email'),
                        'is_open' : 'mobile'
                    })
                    # logic for update pwd in query 
                    user.update_password(user.sms_otp_val,user.id)
                    return request.render('web.login', vals)
    
                if user.default_password and not user.email_otp and not user.sms_otp:
                    vals.update({
                        'login': post.get('email'),
                        'is_open' : 'password'
                    })
                    return request.render('web.login', vals)

                if user.email_otp:
                    
                    vals.update({
                        'user' : user,
                        'is_open': 'email'
                    })
                    return request.render('lee_auth.lee_auth_login', vals)
                if not  user.email_otp and user.sms_otp:
                    vals.update({
                        'user' : user,
                        'is_open': 'mobile'
                    })

                    return request.render('lee_auth.lee_auth_login', vals)
                
            vals.update({
                'payment_redirect': '/shop/checkout',
                'login': post.get('email')    
            })
            encoded_query_string = urlencode(vals)
            return request.redirect('/web/signup?' + encoded_query_string)
        return request.render('ct_web_checkout.check_email_exist', vals)


    @http.route(['/lee-auth-login'], type='http', auth="public", website=True)
    def lee_auth_login(self, **post):
        vals = {}
        user = False
        IrConfigParam = request.env['ir.config_parameter']
        vals.update({
            'signup_enabled': IrConfigParam.sudo().get_param('auth_signup.allow_uninvited') == 'True',
            'reset_password_enabled': IrConfigParam.sudo().get_param('auth_signup.reset_password') == 'True',
        })
        if post.get('user'):
            user = request.env['res.users'].sudo().search([('id', '=', int(post.get('user')))])
        if post.get('is_open') == 'email':
            if user.email_otp_val == post.get('security_code_email'):
                if user.sms_otp and user.default_password:
                    vals.update({
                            'user' : user,
                            'is_open': 'mobile'
                    })
                    return request.render('lee_auth.lee_auth_login', vals)
                if user.sms_otp and not  user.default_password:
                    vals.update({
                        'login': user.login,
                        'is_open' : 'mobile'
                    })
                    user.update_password(user.sms_otp_val,user.id)
                    return request.render('web.login', vals)
            else:
                vals.update({
                            'user' : user,
                            'is_open': 'email',
                            'warning': True,
                            'msg': 'Plase Enter Valid Email OTP'
                })
                return request.render('lee_auth.lee_auth_login', vals)

        if post.get('is_open') == 'mobile':
            if user.sms_otp_val == post.get('security_code_mobile'):
                if user.default_password:
                    vals.update({
                        'user':user,
                        'login': user.login,
                        'is_open' : 'password'
                    })
                    return request.render('web.login', vals)
            else:
                vals.update({
                            'user' : user,
                            'is_open': 'mobile',
                            'warning': True,
                            'msg': 'Plase Enter Valid Mobile OTP'
                })
        if post.get('is_open') == 'password':
            vals.update({
                'login': post.get('login'),
                'is_open' : 'password'
            })
            return request.render('web.login', vals)
        return request.render('lee_auth.lee_auth_login', vals)
