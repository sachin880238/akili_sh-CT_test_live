from odoo import models, fields, tools, api
from datetime import datetime, timedelta, date
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, ValidationError
from skpy import Skype, SkypeContacts,SkypeChats
import re
import logging
import html2text
import urllib.request
class Message(models.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _rec_name = 'email_from'
    _inherit = 'mail.message'
    
    _description = 'Message'

    AVAILABLE_PRIORITIES = [
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
        ]

    _order = "sequence"


    skype_id = fields.Char('Skpe ID')
    skype_password = fields.Char('Skype Password')
    send_to = fields.Char('To be Send')
    sequence = fields.Integer(string='sequence', help="Gives the sequence order when displaying a list of Messages.")
    file_attached = fields.Binary(string="Attachments")
    channel_id = fields.Many2one('communication.channel', string='Channel')
    channel_name = fields.Char('Channel name',related="channel_id.name")
    author_name = fields.Char(compute='get_full_author_name')
    identifier = fields.Many2one('ct.directory',string ='Identifier')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_msg_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_msg_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
   

    def get_document_name(self):
        for message in self:
            if message.model and message.res_id:
                record = self.env[message.model].browse(message.res_id)
                message.document_name = record.name

    res_id = fields.Integer('Related Document ID', index=True, required=False, store=True)
    document_name = fields.Char(compute='get_document_name')

    @api.one
    @api.constrains('state')
    def onchange_state_color(self):
        if self.state == "draft":
            self.color = "#6ABD25"
            if self.state == "sent":
                self.color = "#FFF100"
            if self.state == "failed":
                self.color = "#FFF100"

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        return super(Message, self).copy(default=default)

    @api.model
    def _get_default_from(self):
        res = super(Message, self)._get_default_from()
        if self.env.user.partner_id.name and self.env.user.partner_id.company_id:
            res  = self.env.user.partner_id.name + ',' + " " +  self.env.user.partner_id.company_id.name
        else:
            res = self.env.user.partner_id.name
        return res


    state = fields.Selection([
        ('in', 'INBOX'),
        ('hold', 'HOLD'),
        ('draft','DRAFT'),
        ('out','OUTBOX'),
        ('sent','SENT'),
        ('saved','SAVED'),
        ('trash','TRASH')
        ], default = 'in')

    @api.multi
    def attach_file(self):
        return True

    file_count = fields.Integer(string='Attachment')    
    tag = fields.Char(string="Tag")
    date = fields.Datetime('Date', default=fields.Datetime.now)
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Priority', index=True, default='1')
    time = fields.Char(string="Time", compute='get_current_time')
    email_from = fields.Char(
        'From', default=_get_default_from,
        help="Email address of the sender. This field is set when no matching partner is found and replaces the author_id field in the chatter.")

    @api.model
    def create(self, values):
        res = super(Message, self).create(values)
        for rec in res :
            if rec.message_type == 'notification':
                notification = False
                notification = self.env['communication.channel'].search([('name','=','System Notification')])
                rec.channel_id = notification
                if rec.env.user.partner_id and rec.env.user.partner_id.company_id:
                    rec.email_from = rec.env.user.partner_id.name + ',' + " " +  rec.env.user.partner_id.company_id.name
                else:
                    rec.email_from = rec.env.user.partner_id.name
            if rec.message_type == 'comment':
                notification = False
                notification = self.env['communication.channel'].search([('name','=','Comment')])
                rec.channel_id = notification
            if rec.message_type == 'email':
                notification = False
                notification = self.env['communication.channel'].search([('name','=','Email')])
                rec.channel_id = notification
        return res

    @api.depends('author_id')
    def get_full_author_name(self):
        for rec in self:
            if rec.author_id and rec.author_id.company_id:
                rec.author_name = rec.author_id.name + ', ' + " " + rec.author_id.company_id.name
            elif rec.author_id:
                rec.author_name = rec.author_id.name
            elif rec.author_id.company_id:
                rec.author_name = rec.author_id.company_id.name

    
    @api.multi
    def get_current_time(self):
        for rec in self:
            if rec.date :
                rec.time = rec.date.time()

    @api.multi
    def msg_hold(self):
        self.write({'state': 'hold'})

    @api.multi
    def reply_msg(self):
        self.copy()
        self.write({'state': 'draft'})
        return True

    @api.multi
    def msg_forward(self):
        self.copy()
        self.write({'state': 'draft'})
        return True

    @api.multi
    def msg_duplicate(self):
        self.copy()
        self.write({'state': 'draft'})
        return True

    @api.multi
    def msg_filed(self):
        self.write({'state': 'filed'})
        return True

    @api.multi
    def msg_trash(self):
        self.write({'state': 'trash'})
        return True


    # @api.one
    # @api.constrains('channel_id')
    # def whatsapp_msg(self):
    #     if self.channel_id.name == 'Whatsapp Chat':
    # def send_msg(self):
    #     return {'type': 'ir.actions.act_window',
    #         'name': _('Whatsapp Message'),
    #         'res_model': 'whatsapp.message.wizard',
    #         'target': 'new',
    #         'view_mode': 'form',
    #         'view_type': 'form',
            # 'context': {'default_user_id': self.id},
                # }

    @api.multi
    def msg_send(self):
        from ringcentral import SDK
        import os
        
        RINGCENTRAL_CLIENTID = "5xUXmLkbQiiEjMNBGf1s8Q"
        RINGCENTRAL_CLIENTSECRET = 'DWy3wAYNTM-TGiERj4gztABp1RngBRRC6tJgbwGGJfpw'
        RINGCENTRAL_SERVER = 'https://platform.devtest.ringcentral.com'

        RINGCENTRAL_USERNAME = '+13128589984'
        RINGCENTRAL_PASSWORD = 'Akili@123'
        RINGCENTRAL_EXTENSION = "101"



        # Code to connect skype user
        if self.channel_id.name == 'Skype':
            if self.send_to:
                try:
                  sk = Skype(self.skype_id, self.skype_password)
                except:
                  raise ValidationError('Please Enter A valid Skype email and password')
                logging.info('connected')
                ch = sk.contacts[self.send_to].chat # 1-to-1 conversation
                ch.sendMsg(html2text.html2text(self.body)) # plain-text message
                
            else:
               raise ValidationError('Please Select Channel Type  As "Skype"')
        elif self.channel_id.name == 'Chat':

            rcsdk = SDK(RINGCENTRAL_CLIENTID, RINGCENTRAL_CLIENTSECRET, RINGCENTRAL_SERVER)
            platform = rcsdk.platform()
            logging.info('Connected')
            platform.login(RINGCENTRAL_USERNAME,RINGCENTRAL_EXTENSION, RINGCENTRAL_PASSWORD)
            resp = platform.post('/restapi/v1.0/account/~/extension/~/sms',
                    {
                        'from' : { 'phoneNumber': RINGCENTRAL_USERNAME },
                        'to'   : [ {'phoneNumber': '+14109086811'} ],
                        'text' : html2text.html2text(self.body)
                    })
            
            jsonObj = resp.json()
            logging.info('Object Response'+'\n'+str(jsonObj.__dict__)) 
            # loggin.info(jsonObj.readStatus)
            # loggin.info(jsonObj.availability)


        elif self.channel_id.name == 'Phone':
            rcsdk = SDK(RINGCENTRAL_CLIENTID, RINGCENTRAL_CLIENTSECRET, RINGCENTRAL_SERVER)
            platform = rcsdk.platform()
            platform.login(RINGCENTRAL_USERNAME,RINGCENTRAL_EXTENSION, RINGCENTRAL_PASSWORD)
            logging.info('Connected')
            # For Ringout
            resp = platform.post('/restapi/v1.0/account/~/extension/~/ring-out',
                    {
                      'from' : { 'phoneNumber': "+13127679002*0" },
                      'to'   : { 'phoneNumber': RINGCENTRAL_USERNAME },
                      'playPrompt' : True
                    })  
            jsonObj = resp.json()
            logging.info('CALL Status'+'\n'+str(jsonObj.status.__dict__))
            # For ALL CALL LOGS
            """ params = {
                'view': 'Detailed'
            }
            resp = platform.get('/restapi/v1.0/account/~/extension/~/call-log', params)
            jsonObj = resp.json()
            for record in resp.json().records:
                logging.info("Call type: " +str(record.type))
            logging.info('Response of Call Log'+'\n'+str(record.__dict__)) """

        elif self.channel_id.name == 'Fax':
            # For Fax 
            rcsdk = SDK(RINGCENTRAL_CLIENTID, RINGCENTRAL_CLIENTSECRET, RINGCENTRAL_SERVER)
            platform = rcsdk.platform()
            platform.login(RINGCENTRAL_USERNAME,RINGCENTRAL_EXTENSION, RINGCENTRAL_PASSWORD)
            logging.info('Connected')
            attachment = (
            'test.png',
            urllib.request.urlopen('https://developers.ringcentral.com/assets/images/ico_case_crm.png').read(),
            'image/png'
            )
            builder = rcsdk.create_multipart_builder()
            builder.set_body({
            'to': [{'phoneNumber': '+14103661202'}],
            'faxResolution': 'High'
            })
            builder.add(attachment)
            request = builder.request('/account/~/extension/~/fax')
            response = platform.send_request(request)
            logging.info('Object Response'+'\n'+str(response.__dict__))

        self.write({'state': 'out'})
        return True

    @api.multi
    def msg_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def msg_open(self):
        self.write({'state': 'in'})
        return True

class CommunicationChannel(models.Model):

    _name = 'communication.channel'
    _description = 'Communication Channel'

    name = fields.Char(string="Name")
