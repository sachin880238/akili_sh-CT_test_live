# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import date,datetime


class ResCompany(models.Model):
    _inherit = "res.company"
    
    state_code = fields.Char(string="State",related="state_id.code")
    country_code = fields.Char(related='country_id.code', string='Country Code', readonly=True)
    state = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')],
                             string='Status', default='draft')
    desc = fields.Many2one('customer.description', 'Description')
    icon_letters = fields.Char("Icon", size=2)
    street3 = fields.Char()
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_company_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_company_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
    
    def activate_company(self):
        self.state = 'active'

    def deactivate_company(self):
        self.state = 'inactive'

    def reset_to_draft(self):
        self.state = 'draft'
    
    complete_address = fields.Text(string="Address", compute="get_complete_address")
    same_as_country = fields.Boolean(string="Same Country")

    @api.depends('street','street2','street3','city','state_id','zip','country_id')
    def get_complete_address(self):
        complete_address = ''
        for rec in self:
            if rec.street: 
                complete_address += rec.street
                if any([rec.street2,rec.street3,rec.city, rec.state_id, rec.zip, rec.country_id]):
                    complete_address += '\n'
            if rec.street2: 
                complete_address += rec.street2
                if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.street3: 
                complete_address += rec.street3
                if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.city and rec.state_id and rec.zip : 
                complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.city and rec.state_id and not rec.zip : 
                complete_address += rec.city + ' ' + rec.state_id.code
                if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.city and rec.zip and not rec.state_id : 
                complete_address += rec.city + ' ' + rec.zip
                if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.state_id and rec.zip and not rec.city : 
                complete_address += rec.state_id.code + ' ' + rec.zip
                if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.city and not rec.state_id and not rec.zip: 
                complete_address += rec.city
                if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.state_id and not rec.city and not rec.zip: 
                complete_address += rec.state_id.code
                if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.zip and not rec.city and not rec.state_id: 
                complete_address += rec.zip
                if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                    complete_address += '\n'
            if rec.country_id:
                complete_address += rec.country_id.name

            rec.complete_address = str(complete_address)
    
    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()
    
    lang = fields.Selection(_lang_get, string='Language', default=lambda self: self.env.lang,
                            help="All the emails and documents sent to this contact will be translated in this language.")
    primary_telephone = fields.Char(string="Primary Telephone")
    primary_tel_type = fields.Many2one('communication.type', string='Communication Type')
    alternate_communication_1 = fields.Char(string="Alternate Communication 1")
    alternate_commu_type_1 = fields.Many2one('communication.type', string='Communication Type')
    alternate_communication_2 = fields.Char(string="Alternate Communication 2")
    alternate_commu_type_2 = fields.Many2one('communication.type', string='Communication Type')
    get_email = fields.Char("Email", compute='get_comm_attributes')
    get_telephone = fields.Char("Telephone", compute='get_comm_attributes')
    get_other1 = fields.Char("Other", compute='get_comm_attributes')
    get_other2 = fields.Char("Other", compute='get_comm_attributes')
    get_website = fields.Char("Website", compute='get_comm_attributes')
    get_lang = fields.Char("Language", compute='get_comm_attributes')


    @api.multi
    def get_comm_attributes(self):
        for rec in self:
            if rec.email:
                rec.get_email = rec.email
            if rec.phone:
                if rec.primary_tel_type:
                    telephone = rec.phone + " ("+ rec.primary_tel_type.name + ")"
                    rec.get_telephone = str(telephone)
                else:
                    rec.get_telephone = rec.phone
            if rec.alternate_communication_1:
                if rec.alternate_commu_type_1:
                    other1 = rec.alternate_communication_1 + " ("+ rec.alternate_commu_type_1.name + ")"
                    rec.get_other1 =  str(other1)
                else:
                    rec.get_other1 =  rec.alternate_communication_1 
            if rec.alternate_communication_2:
                if rec.alternate_commu_type_2:
                    other2 =  rec.alternate_communication_2 + " ("+ rec.alternate_commu_type_2.name + ")"
                    rec.get_other2 = str(other2)
                else:
                    rec.get_other2 = rec.alternate_communication_2 
            if rec.website:
                rec.get_website = rec.website
            if not rec.website:
                rec.get_website = ""
            if rec.lang:
                lang = self.env['res.lang'].search([('code','=',rec.lang)]).name
                rec.get_lang = lang

    
    company_addresses_ids = fields.One2many('res.partner', 'company_address_id', string="Address", help='It contains company addresses')
    team_ids = fields.One2many('crm.team', 'company_id', string="Teams", help='It contains Teams')
    street_address = fields.Char('Address', compute='_compute_street_address')

    @api.depends('street', 'street2', 'street3')
    def _compute_street_address(self):
        for company in self:
            if all([company.street, company.street2, company.street3]):
                company.street_address = company.street + ', ' + company.street2 + ', ' + company.street3
            elif all([company.street, company.street2]):
                company.street_address = company.street + ', ' + company.street2
            elif all([company.street, company.street3]):
                company.street_address = company.street + ', ' + company.street3
            elif all([company.street2, company.street3]):
                company.street_address = company.street2 + ', ' + company.street3
            else:
                company.street_address = company.street or company.street2 or company.street3  or ''
            
    @api.multi
    def check_address_contrainst(self,address_list, default_line=False):      
        if len(address_list) > 1:
            if default_line in address_list:
                if default_line.default_address:
                    for line in address_list:
                        if line != default_line:
                            line.default_address = False
                else:
                    if all(not line.default_address for line in address_list):
                        for line in address_list:
                            if line != default_line:
                                line.default_address = False
        return {'msg': False}
                    
    @api.onchange('company_addresses_ids')
    def onchange_child_ids(self):
        contact_list = []
        billing_list = []
        shipping_list = []
        default_line = False
        for line in self.company_addresses_ids:
            if line.current_default:
                default_line = line
            if line.type_extend == 'contact':
                contact_list.append(line)
                continue
            if line.type_extend == 'invoice':
                billing_list.append(line)
                continue
            if line.type_extend == 'delivery':
                shipping_list.append(line)
                continue

        if default_line in contact_list:
            result = self.check_address_contrainst(contact_list,default_line)
            default_line.current_default = False

        if default_line in shipping_list:            
            result = self.check_address_contrainst(shipping_list,default_line)
            default_line.current_default = False
        
        if default_line in billing_list:
            result = self.check_address_contrainst(billing_list,default_line)
            default_line.current_default = False

    @api.onchange('icon_letters')
    def set_upper(self):
        if self.icon_letters:
            self.icon_letters = str(self.icon_letters).upper()

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    company_address_id = fields.Many2one('res.company')
    is_company_address = fields.Boolean(string='Is Company', help='It used to find company addresses')
    same_as_company = fields.Boolean(string="Same as Company")

    @api.onchange('same_as_company')
    def onchange_use_company_communication(self):
        if self.is_company_address and self.same_as_company and self.company_address_id:
            self.email = self.company_address_id.email
            self.phone =  self.company_address_id.phone
            self.primary_tel_type = self.company_address_id.primary_tel_type
            self.primary_telephone = self.company_address_id.primary_telephone
            self.alternate_communication_1 = self.company_address_id.alternate_communication_1
            self.alternate_commu_type_1 = self.company_address_id.alternate_commu_type_1
            self.alternate_communication_2 = self.company_address_id.alternate_communication_2
            self.alternate_commu_type_2 = self.company_address_id.alternate_commu_type_2
            self.website = self.company_address_id.website
            self.street = self.company_address_id.street
            self.street2 = self.company_address_id.street2
            self.street3 = self.company_address_id.street3
            self.city = self.company_address_id.city
            self.state_id = self.company_address_id.state_id.id
            self.zip = self.company_address_id.zip
            self.country_id = self.company_address_id.country_id.id
            self.icon_letters = self.company_address_id.icon_letters
            self.desc = self.company_address_id.desc
            
    @api.onchange('country_id','zip','state_id','city','street','street2','street3','email', 'phone', 'website', 'primary_tel_type', 'alternate_communication_1', 'alternate_communication_2', 'alternate_commu_type_1', 'alternate_commu_type_2')
    def onchange_comm(self):
        if self.is_company_address and self.same_as_company:
            if self.street != self.company_address_id.street:
                self.same_as_company = False
            if self.street2 != self.company_address_id.street2:
                self.same_as_company = False
            if self.street3 != self.company_address_id.street3:
                self.same_as_company = False
            if self.city != self.company_address_id.city:
                self.same_as_company = False
            if self.state_id != self.company_address_id.state_id:
                self.same_as_company = False
            if self.zip != self.company_address_id.zip:
                self.same_as_company = False
            if self.country_id != self.company_address_id.country_id:
                self.same_as_company = False
            if self.email != self.company_address_id.email :
                self.same_as_company = False
            if self.primary_tel_type != self.company_address_id.primary_tel_type :
                self.same_as_company = False
            if self.alternate_communication_1 != self.company_address_id.alternate_communication_1 :
                self.same_as_company = False
            if self.alternate_communication_2 != self.company_address_id.alternate_communication_2 :
                self.same_as_company = False
            if self.alternate_commu_type_1 != self.company_address_id.alternate_commu_type_1 :
                self.same_as_company = False
            if self.alternate_commu_type_2 != self.company_address_id.alternate_commu_type_2 :
                self.same_as_company = False
            if self.phone != self.company_address_id.phone :
                self.same_as_company = False
            if self.website != self.company_address_id.website :
                self.same_as_company = False
            if self.desc != self.company_address_id.desc :
                self.same_as_company = False
