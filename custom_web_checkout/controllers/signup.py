# -*- coding: utf-8 -*-
import datetime
import logging
import random
from odoo import http, tools, _
from odoo.http import request
import werkzeug
import re
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type , NumberParseException
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import login_and_redirect


_logger = logging.getLogger(__name__)


class AuthSignupHome(Home):

    def send_email_for_login(self, user):
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        token =  ''.join(random.SystemRandom().choice(chars) for i in range(20))

        user.token = token
        user.token_create_time = datetime.datetime.now()
        user.oauth_access_token = token
        template = request.env.ref('custom_web_checkout.login_by_token_email')
        res = template.sudo().with_context(lang=user.lang).send_mail(user.id)
        _logger.info("Login Link send to customer <%s> to <%s>", user.login, user.email)
        return True

    def custom_signup_redirect(self, qcontext, *args, **kw):
        if qcontext.get('telephone_number') or qcontext.get('password'):
            return super(AuthSignupHome, self).web_login(*args, **kw)
        else:
            user_id = request.env.user
            request.session.logout(keep_db=True)
            self.send_email_for_login(user_id)
            vals = {'user': user_id}
            return request.render('custom_web_checkout.greetings_after_signup', vals)

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        communication_phone_type = request.env['communication.type'].sudo().search([('for_phone', '=', True)])
        communication_other_type = request.env['communication.type'].sudo().search([('for_other', '=', True)])
        country = request.env['res.country'].sudo().search([('code','=','US')])
        countries = request.env['res.country'].sudo().search([])
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if not kw.get('password'):
                    pawd_random = str(random.randrange(1000,9999))
                    request.params['password'] =  pawd_random
                    qcontext.update({'password': pawd_random})
                    self.do_signup(qcontext)
                    qcontext.pop('password')
                else:
                    self.do_signup(qcontext)
                res = self.custom_signup_redirect(qcontext, *args, **kw)
                return res
            except: # (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("This User is Already Exists.")
                else:
                    if not qcontext['email_address'] or not qcontext['telephone_number'] or not qcontext['password'] and qcontext['login']:
                    # if not qcontext['email_address'] or not qcontext['telephone_number'] or not qcontext['password'] and qcontext['login']:
                        # _logger.error(e.message)
                        qcontext['error'] = _("Please Enter Email Mobile or Password.")
                    # else:
                    #     _logger.error(e.message)
                    #     qcontext['error'] = _(e.messag e)

        qcontext.update({
            'country': country,
            'countries': countries,
            'communication_phone_type': communication_phone_type,
            'communication_other_type': communication_other_type,
            'payment_redirect': kw.get('payment_redirect'),
            'redirect': (kw.get('payment_redirect')) or request.params.get('redirct'),
            'company_type': kw.get('company_type')
        })
        return request.render('auth_signup.signup', qcontext)


    def get_auth_signup_qcontext(self):

        if request.params.items() and request.params.get('telephone_number'):
            try:
                carrier._is_mobile(number_type(phonenumbers.parse(request.params['telephone_number'])))
            except NumberParseException:
                request.params['error'] = _("Please Enter Valid Mobile Number")
        if request.params.items() and request.params.get('login'):
            if not tools.single_email_re.match(request.params.get('login')):
                request.params['error'] = _("Please Enter Valid Email")

        if request.params.items() and request.params.get('email_address'):
            if not tools.single_email_re.match(request.params.get('email_address')):
                request.params['error'] = _("Please Enter Valid Email")

        if request.params.items() and request.params.get('telephone_number') and request.params.get('login') == '':
            request.params['login'] = request.params.get('telephone_number')

        qcontext = request.params.copy()
        qcontext.update(self.get_auth_signup_config())

        if qcontext.get('token'):
            try:
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext


    def do_signup(self, qcontext):
        """ Override do_signup for Create User & Partner with Extra field Mobile.
        """
        values = { 
            key: qcontext.get(key) for key in (
                'login', 'name', 'password',
                'telephone_number', 'email_address',
                'street2', 'street', 'city', 'state_id',
                'zip', 'country_id', 'phone',
                'primary_tel_type', 'alternate_communication_1',
                'alternate_commu_type_1', 'alternate_communication_2', 
                'alternate_commu_type_2')
            }

        if qcontext.get('company_type') == 'company':
            values.update({
                'company_type': "company",
                'name': qcontext.get('comapny_name') or qcontext.get('name'),
                'is_company': True
            })

        values.update({'copy_contacts':True,'customer':True})

        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang    
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()


    @http.route('/web/maillogin', type='http', auth='public', website=True)
    def mail_login(self, *args, **post):
        if post and post.get('token') and post.get('id'):
            user = request.env['res.users'].browse(int(post.get('id')))
            return login_and_redirect(request.db, user.login, post.get('token'), '/')
        return request.redirect('/web/login')
