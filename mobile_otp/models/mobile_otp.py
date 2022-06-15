from odoo import api, fields, models, _
import logging
import datetime
import time
import string
import random

from odoo.exceptions import UserError

try:
    import plivo
except :
    raise UserError(_('Library plivo not installed Try: sudo pip install plivo '))


class PlivoConnection(models.Model):
    _name = "plivo.connection"
    _description = "Plivo Connection"

    name = fields.Char('Root URL', default="https://www.plivo.com" )
    credential = fields.Boolean("Show/Hide Credentials Tab ")
    user = fields.Char('User Auth ID', required=True, )
    password = fields.Char('User Auth Token', required=True, )
    message = fields.Char('Message', required=True, default="is your Conservation login Password")
    email = fields.Char('Email', required=True, default="is your Conservation login Password")
    src = fields.Char('Sender', required=True, )


class MobileOTP(models.Model):
    _name = "mobile.otp"
    _description = "Mobile Otp"
   
    name = fields.Char("Mobile OTP")
    send_to = fields.Char(string='Send To')
    validity = fields.Integer(string="Valididty in Minutes")
    expiry_date = fields.Datetime("Expiry Date")
    response = fields.Char("Response")
    email = fields.Char("Email")
    company_id = fields.Many2one("res.company", string="Company", default=1)
    user_id = fields.Many2one("res.users", string="User" )
  
    def get_new_otp(self):
        chars = string.ascii_letters + string.digits
        pwdSize = 6
        res = "".join((random.choice(chars)) for x in range(pwdSize))

        return res

    def get_email_message(self): 
        plivo_id = self.env['plivo.connection'].search([])
        if not plivo_id:
            raise UserError(_('Kindly Configure plivo Account to send OTP !! '))
        otp = self.get_new_otp()

        email_message = self.name + ' ' + plivo_id.message

        return email_message


    @api.multi
    def action_otp_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('mobile_otp', 'email_template_otp')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'mobile.otp',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order"
        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    @api.model
    def message_get_reply_to(self, res_ids, default=None):
        otp = self.sudo().browse(res_ids) 
        return "noreply@conservationtechnologies.com"


    def send_otp_email(self): 
        vals ={}
        template_obj = self.env['mail.template']
        temp_id = template_obj.search([('name','=','OTP Email')])
        if self.email:
            #email_wiz_id = self.action_otp_send()
            #test = email_wiz_id.send_mail(auto_commit=False) 
            test = temp_id.send_mail(self.id, force_send=False, raise_exception=False, email_values=False) 
            return test
        else:
            return False
            

    def send_otp(self, mobile, otp):

        plivo_id = self.env['plivo.connection'].search([])
        if not plivo_id:
            # raise UserError(_('Kindly Configure plivo Account to send SMS !! '))
            return True
        auth_id = plivo_id.user
        auth_token = plivo_id.password

        p = plivo.RestClient(auth_id, auth_token)

        message_created = p.messages.create(src = plivo_id.src, dst = mobile, text = otp + ' ' + plivo_id.message)

        #params = {
        #   'src': plivo_id.src , # Sender's phone number with country code
        #   'dst' : mobile, # Receiver's phone Number with country code
        #   'text' : otp + ' ' + plivo_id.message, # Your SMS Text Message - English
        #   'method' : 'POST' # The method used to call the url
        #         }
        #response = p.send_message(params)
        return message_created
        
         
    @api.model
    def create(self, vals):
        # vals['name'] = self.get_new_otp() 
        if not vals['send_to'] and not vals['email']:
            raise UserError(_('Send to Mobile no is required or Send to email is required!! '))
        if not vals['validity']:
            raise UserError(_('validity of the OTP is required !! '))
        # Here Need to set OTP as user password
        if vals['send_to']:
            vals['response'] = self.send_otp(vals['send_to'], vals['name']) 
        res = super(MobileOTP, self).create(vals)
        return res
