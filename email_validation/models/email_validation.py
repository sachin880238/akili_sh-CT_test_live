import re
import dns.resolver
from odoo import models, api, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('email')
    def get_email_address(self):
        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
        for rec in self:
            if rec.email:
                addressToVerify = str(rec.email)
                match = re.match(regex, addressToVerify)
                if match is None:
                    rec.valid_email = False
                    rec.email_address = rec.email
                else:
                    rec.valid_email = True
                    rec.email_address = rec.email
                    splitAddress = addressToVerify.split('@')
                    domain = str(splitAddress[1])
                    try:
                        rec.valid_email = True
                        records = dns.resolver.query(domain, 'MX')
                        mxRecord = records[0].exchange
                        mxRecord = str(mxRecord)
                    except:
                        rec.valid_email = False

    valid_email = fields.Boolean('Is Valid', compute='get_email_address', store=True)
    email_address = fields.Char('Email', compute='get_email_address', store=True)

    @api.model
    def create(self, vals):
        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
        is_valid = None
        
        for rec in self:
            if rec.email:
                addressToVerify = str(rec.email)
                match = re.match(regex, addressToVerify)
                if match is None:
                    rec.valid_email = False
                    rec.email_address = self.email
                else:
                    rec.valid_email = True
                    rec.email_address = self.email
                    splitAddress = addressToVerify.split('@')
                    domain = str(splitAddress[1])
                    try:
                        records = dns.resolver.query(domain, 'MX')
                        mxRecord = records[0].exchange
                        mxRecord = str(mxRecord)
                    except:
                        rec.valid_email = False
        res = super(ResPartner, self).create(vals)
        return res

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    @api.depends('email_from')
    def get_email_address(self):
        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'

        is_valid = None
        for rec in self:
            if rec.email_from:
                addressToVerify = str(rec.email_from)
                match = re.match(regex, addressToVerify)
                if match is None:
                    rec.valid_email = False
                    rec.email_address = self.email_from
                else:
                    rec.valid_email = True
                    rec.email_address = self.email_from
                    splitAddress = addressToVerify.split('@')
                    domain = str(splitAddress[1])
                    try:
                        rec.valid_email = True
                        records = dns.resolver.query(domain, 'MX')
                        mxRecord = records[0].exchange
                        mxRecord = str(mxRecord)
                    except:
                        rec.valid_email = False

    valid_email = fields.Boolean('Is Valid', compute='get_email_address', store=True)
    email_address = fields.Char('Email', compute='get_email_address', store=True)

    @api.model
    def create(self,vals):
        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
        is_valid = None
        for rec in self:
            if rec.email_from:
                addressToVerify = str(rec.email_from)
                match = re.match(regex, addressToVerify)
                if match is None:
                    rec.valid_email = False
                    rec.email_address = self.email_from
                else:
                    rec.valid_email = True
                    rec.email_address = self.email_from
                    splitAddress = addressToVerify.split('@')
                    domain = str(splitAddress[1])
                    try:
                        records = dns.resolver.query(domain, 'MX')
                        mxRecord = records[0].exchange
                        mxRecord = str(mxRecord)
                    except:
                        rec.valid_email = False

        res = super(CrmLead,self).create(vals)
        return res
