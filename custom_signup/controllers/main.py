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
from odoo.addons.website.controllers.main import Home
from odoo.addons.web.controllers.main import ensure_db
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import login_and_redirect
from odoo.exceptions import AccessDenied
from odoo.addons.mobile_otp.models.mobile_otp import MobileOTP
from odoo.exceptions import UserError

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

_logger = logging.getLogger(__name__)


class AuthSignupHome(Home):

    def generate_otp_and_send(self, user):
        otp =  ''.join(random.SystemRandom().choice('0123456789') for i in range(6))

        mobile = user.otp_mobile_no
        user.oauth_access_token = otp
        user.token_create_time = datetime.datetime.now()
        user.token_valid = True

        user.otp = otp
        user.otp_create_time = datetime.datetime.now()
        user.otp_valid = True
        _logger.info("OTP <%s> - <%s> of <%s>", user.login, user.email, otp)
        _logger.info("OTP <%s><%s><%s>","\n"*10, otp, "\n"*10)
        vals = {
        'user_id': user.id,
        'send_to': user.otp_mobile_no,
        'name': otp,
        'email': user.email_address,
        'validity': 10,
        'response': False
        }
        creat_record=request.env['mobile.otp'].sudo().search([])
        creat_record.create(vals)

        return otp

    def check_otp(self, user, **kw):
        if ((user.oauth_access_token == kw.get('otp')) and (user.otp == kw.get('otp'))):
            return True
        else:
            return False

    def generate_token(self, user):
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        token =  ''.join(random.SystemRandom().choice(chars) for i in range(20))
        user.oauth_access_token = token
        user.token_create_time = datetime.datetime.now()
        user.token_valid = True
        return token
        

    def send_email_for_login_after_signup(self, user):
        token = self.generate_token(user)
        template = request.env.ref('custom_signup.login_by_token_email_after_signup')
        try:
            template.sudo().with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
        except:
            vals = {'user_rec': user,'flag':False}
            return request.render('custom_signup.greetings_after_email_auth_link', vals)
        _logger.info("Login Link send to customer <%s> to <%s>", user.login, user.email)
        vals = {'user_rec': user,'flag':True}
        return request.render('custom_signup.greetings_after_email_auth_link', vals)

    def signin_email_authenticate(self, user):
        token = self.generate_token(user)
        template = request.env.ref('custom_signup.signin_email_authenticate_mail_template')
        # res = template.sudo().with_context(lang=user.lang).send_mail(user.id)
        template.sudo().with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
        _logger.info("Login Link send to customer <%s> to <%s>", user.login, user.email)
        vals = {'user_rec': user}
        return request.render('custom_signup.greetings_after_email_auth_link', vals)

    def get_quote_signin_send_email(self, user):
        token = self.generate_token(user)
        template = request.env.ref('custom_signup.login_by_token_email_after_get_quote')
        outgoing_mail_exit = request.env['ir.mail_server'].sudo().search([])
        if outgoing_mail_exit:
            template.sudo().with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
            _logger.info("Login Link send to customer <%s> to <%s>", user.login, user.email)
            vals = {'user_rec': user,
                    'flag': 'True'}
            return request.render('custom_signup.greetings_after_email_auth_link', vals)
        else:
            vals = {'user_rec': user,
                    'flag': 'False'}
            return request.render('custom_signup.greetings_after_email_auth_link', vals)
    
    def custom_signup_redirect(self, qcontext, *args, **kw):
        user = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))], limit=1)
        if qcontext.get('password') and not qcontext.get('telephone_number'):
            return super(AuthSignupHome, self).web_login(*args, **kw)
        if qcontext.get('telephone_number'):
            otp = self.generate_otp_and_send(user)
            request.env.cr.commit()
            return login_and_redirect(request.db, user.login, otp, qcontext.get('redirect') or '/')
        else:
            res = self.send_email_for_login_after_signup(user)
            return res

    @http.route(['/send-mail/sign-in'], type='http', auth="public", website=True)
    def send_mail_sign_in(self, redirect=None, **post):
        user = request.env['res.users'].sudo().search([('login', '=', post.get('login'))], limit=1)

        if user:
            user.redirect = redirect
            token = self.generate_token(user)
            template = request.env.ref('custom_signup.general_signin_by_email_template')
            template.sudo().with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
            _logger.info("Login Link send to customer <%s> to <%s>", user.login, user.email)
            vals = {'user_rec': user}
            return request.render('custom_signup.greetings_after_email_auth_link', vals)

    @http.route(['/text-a-new-code'], type='json', auth="public", website=True)
    def text_a_new_code(self, **post):
        user = request.env['res.users'].sudo().search([('login', '=', post.get('login'))], limit=1)

        vals = {}
        if user.otp_mobile_no and user.is_mobile_auth:
            self.generate_otp_and_send(user)
            vals.update({
                'otp_mobile_no': user.otp_mobile_no    
            })
        return vals

    @http.route()
    def web_login(self, redirect=None, **post):
        ensure_db()
        vals = {
            'payment_redirect': redirect or '/my/home',
            'redirect': redirect or '/my/home'
        }

        if not post.get('login'): 
            return request.render('custom_signup.check_email_exist', vals)
        
        user = request.env['res.users'].sudo().search([('login', '=', post.get('login'))], limit=1)
        
        if not user:
            vals.update({
                'login': post.get('login')    
            })
            encoded_query_string = urlencode(vals)
            return request.redirect('/web/signup?' + encoded_query_string)
        
        vals.update({
            'login': post.get('login'),
            'is_email_auth': user.is_email_auth,
            'is_password_auth': user.is_password_auth,
            'is_mobile_auth': user.is_mobile_auth,
            'error': False
        })

        # redirect with appropriate security
        if not user.is_password_auth and not user.is_mobile_auth:
            res = self.get_quote_signin_send_email(user)
            return res

        if user.is_password_auth and not user.is_mobile_auth:
            if not post.get('password'):
                res = request.render('custom_signup.checkout_password', vals)
                return res
            else:
                res = super(AuthSignupHome, self).web_login(redirect, **post)

                if res.qcontext.get('error'):
                    vals.update({
                        'error': res.qcontext.get('error'),
                        'password': post.get('password')
                    })
                    res = request.render('custom_signup.checkout_password', vals)
                    return res
                else:
                    return res

        if not user.is_password_auth and user.is_mobile_auth:
            vals.update({
                'otp_mobile_no': user.otp_mobile_no 
            })
            if not post.get('otp'):
                self.generate_otp_and_send(user)
                res = request.render('custom_signup.checkout_otp', vals)
                return res
            else:
                if self.check_otp(user, **post):
                    res = login_and_redirect(request.db, user.login, post.get('otp'), redirect or '/')
                    user.otp = False
                    return res
                else:
                    vals.update({
                        'otp_mobile_no': user.otp_mobile_no,
                        'error': "Invalid OTP",
                        'otp': post.get('otp')
                    })
                    res = request.render('custom_signup.checkout_otp', vals)
                    return res

        if user.is_password_auth and user.is_mobile_auth:
            if not post.get('password') and not post.get('otp') and not post.get('password_valid'):
                return request.render('custom_signup.checkout_password', vals)
            elif post.get('password') and not post.get('otp'):

                try:
                    user.sudo(user.id)._check_credentials(post.get('password'))
                    vals.update({
                        'otp_mobile_no': user.otp_mobile_no,
                        'password_valid': True,
                    })
                    self.generate_otp_and_send(user)
                    return request.render('custom_signup.checkout_otp', vals)
                except AccessDenied:
                    vals.update({
                        'error': "Invalid Username/Password.",
                        'password': post.get('password')
                    })
                    res = request.render('custom_signup.checkout_password', vals)
                    return res

            elif post.get('otp') or post.get('password_valid'):
                vals.update({
                    'password_valid': post.get('password_valid'),    
                })

                if self.check_otp(user, **post):
                    res = login_and_redirect(request.db, user.login, post.get('otp'), redirect or '/')
                    user.otp = False
                    return res
                else:
                    vals.update({
                        'otp_mobile_no': user.otp_mobile_no,
                        'error': "Invalid OTP",
                        'otp': post.get('otp')
                    })
                    return request.render('custom_signup.checkout_otp', vals)
            
   
    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        communication_phone_type = request.env['communication.type'].sudo().search([('for_phone', '=', True)])
        communication_other_type = request.env['communication.type'].sudo().search([('for_other', '=', True)])
        country = request.env['res.country'].sudo().search([('code','=','US')])
        countries = request.env['res.country'].sudo().search([])
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and not qcontext.get('err') and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                res = self.custom_signup_redirect(qcontext, *args, **kw)
                return res
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("This User is Already Exists.")
                else:
                    self.do_signup(qcontext)
                    _logger.error(e.message)
                    qcontext['error'] = _(e.message)

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

        MANDATORY_SIGNUP_FIELDS = ["name", "street", "city", "state_id", "zip", "country_id", "login", "phone", "primary_tel_type"]
        err = dict()
        error = []

        qcontext = request.params.copy()
        if request.httprequest.method == 'POST':
            for field_name in MANDATORY_SIGNUP_FIELDS:
                if not request.params.get(field_name):
                    err[field_name] = 'missing'

            if request.params.get('telephone_number'):
                try:
                    carrier._is_mobile(number_type(phonenumbers.parse(request.params['telephone_number'])))
                except NumberParseException:
                    request.params['error'] = _("Please Enter Valid Mobile Number")
            if request.params.get('login'):
                if not tools.single_email_re.match(request.params.get('login')):
                    request.params['error'] = _("Please Enter Valid Email")

        qcontext.update(self.get_auth_signup_config())
        qcontext.update({
            'err': err,
            'postal_code': request.params.get('zip')
        })

        if qcontext.get('token'):
            try:
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def _signup_with_values(self, token, values):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        # uid = request.session.authenticate(db, login, password)
        # if not uid:
        #     raise SignupError(_('Authentication Failed.'))
        # else:
        #     group_id = request.env['ir.model.data'].sudo().get_object('base', 'group_user')
        #     group_id.write({'users': [(4, uid)]})


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
                'alternate_commu_type_2', 'redirect')
            }

        if qcontext.get('company_type') == 'company':
            values.update({
                'company_type': "company",
                'name': qcontext.get('comapny_name') or qcontext.get('name'),
                'is_company': True
            })

        if qcontext.get('login'):
            values.update({'is_email_auth': True,
                'is_password_auth': False
                })
        if qcontext.get('password'):
            values.update({'is_password_auth': True})
        else:
            pawd_random = str(random.randrange(1000,9999))
            values.update({'password': pawd_random})   
        if qcontext.get('telephone_number'):
            values.update({
                'is_mobile_auth': True,
                'otp_mobile_no': qcontext.get('telephone_number')
            })
        values.update({'copy_contacts':True,'customer':True})

        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang

        # if not values.get('is_password_auth') and not values.get('is_mobile_auths'):
        #     db, login, password = request.env['res.users'].sudo().signup(values, qcontext.get('token'))
        # else:
        self._signup_with_values(qcontext.get('token'), values)

        # db, login, password = request.env['res.users'].sudo().signup(values, qcontext.get('token'))
        # uid = request.session.authenticate(db, login, password)
        # request.env.cr.commit()

        # group_id = self.env['ir.model.data'].sudo().get_object('base', 'group_user')
        # group_id.write({'users': [(4, uid)]})


    @http.route('/web/maillogin', type='http', auth='public', website=True)
    def mail_login(self, *args, **post):

        if post and post.get('token') and post.get('id'):
            user = request.env['res.users'].sudo().browse(int(post.get('id')))
            if (user.sudo().oauth_access_token and user.sudo().token_valid):
                user.token_valid = False
                return login_and_redirect(request.db, user.login, post.get('token'), post.get('redirect_url') or '/')
        return request.redirect('/web/login')
