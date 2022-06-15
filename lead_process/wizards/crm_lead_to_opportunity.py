# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

    
class LeadMergePartner(models.TransientModel):
    _name = 'lead.merge.partner'
    _description = 'Lead Merge Partner'

    found_customer = fields.Char("Contact")
    lead_id = fields.Many2one("crm.lead", string="Lead")
    contact_id = fields.Many2one("res.partner", string="Customer")
    l_name = fields.Char("Name")
    l_company = fields.Char("Company")
    l_street = fields.Char("Street")
    l_street2 = fields.Char("Street2")
    l_city = fields.Char('City')
    l_state = fields.Char('State')
    l_zip = fields.Char("Zipcode")
    l_country = fields.Char("Country")
    l_email = fields.Char("Email")
    l_tphone = fields.Char("Telephone")
    l_primary_tel_type = fields.Many2one('communication.type', string="Telephone Type")

    l_alternate_communication_1 = fields.Char(string="Other")
    l_alternate_commu_type_1 = fields.Many2one('communication.type', string="Other Type")

    l_alternate_communication_2 = fields.Char(string="Other")
    l_alternate_commu_type_2 = fields.Many2one('communication.type', string="Other Type")

    # l_fax = fields.Char("Fax")
    # l_other = fields.Char("Other")

    l_website = fields.Char("Website")
    l_lang = fields.Char("Language")
    l_desc = fields.Char("Description")


    name_f = fields.Boolean("Name")
    company_f = fields.Boolean("Company")
    street_f = fields.Boolean("Street")
    street2_f = fields.Boolean("Street2")
    city_f = fields.Boolean('City')
    state_f = fields.Boolean('State')
    zip_f = fields.Boolean("Zipcode")
    country_f = fields.Boolean("Country")
    email_f = fields.Boolean("Email")
    tphone_f = fields.Boolean("Telephone")
    primary_tel_type_f = fields.Boolean("Telephone Type")

    alternate_communication_1_f = fields.Boolean("Other")
    alternate_commu_type_1_f = fields.Boolean("Other Type")

    alternate_communication_2_f = fields.Boolean("Other")
    alternate_commu_type_2_f = fields.Boolean("Other Type")

    # fax_f = fields.Boolean("Fax")
    # other_f = fields.Boolean("Other")

    website_f = fields.Boolean("Website")
    lang_f = fields.Boolean("Language")
    desc_f = fields.Boolean("Description")  

    l_name_f = fields.Boolean("Name")
    l_company_f = fields.Boolean("Company")
    l_street_f = fields.Boolean("Street")
    l_street2_f = fields.Boolean("Street2")
    l_city_f = fields.Boolean('City')
    l_state_f = fields.Boolean('State')
    l_zip_f = fields.Boolean("Zipcode")
    l_country_f = fields.Boolean("Country")
    l_email_f = fields.Boolean("Email")
    l_tphone_f = fields.Boolean("Telephone")
    l_primary_tel_type_f = fields.Boolean("Telephone Type")

    l_alternate_communication_1_f = fields.Boolean("Other")
    l_alternate_commu_type_1_f = fields.Boolean("Other Type")

    l_alternate_communication_2_f = fields.Boolean("Other")
    l_alternate_commu_type_2_f = fields.Boolean("Other Type")

    # l_fax_f = fields.Boolean("Fax")
    # l_other_f = fields.Boolean("Other")

    l_website_f = fields.Boolean("Website")
    l_lang_f = fields.Boolean("Language")
    l_desc_f = fields.Boolean("Description") 


    c_name = fields.Char("Name")
    c_company = fields.Char("Company")
    c_street = fields.Char("Street")
    c_street2 = fields.Char("Street2")
    c_city = fields.Char('City')
    c_state = fields.Char('State')
    c_zip = fields.Char("Zipcode")
    c_country = fields.Char("Country")
    c_email = fields.Char("Email")
    c_tphone = fields.Char("Telephone")
    c_primary_tel_type = fields.Many2one('communication.type', string="Telephone Type")

    c_alternate_communication_1 = fields.Char(string="Other")
    c_alternate_commu_type_1 = fields.Many2one('communication.type', string="Other Type")

    c_alternate_communication_2 = fields.Char(string="Other")
    c_alternate_commu_type_2 = fields.Many2one('communication.type', string="Other Type")

    # c_fax = fields.Char("Fax")
    # c_other = fields.Char("Other")

    c_website = fields.Char("Website")
    c_lang = fields.Char("Language")
    c_desc = fields.Char("Description") 

    c_name_f = fields.Boolean("Name")
    c_company_f = fields.Boolean("Company")
    c_street_f = fields.Boolean("Street")
    c_street2_f = fields.Boolean("Street2")
    c_city_f = fields.Boolean('City')
    c_state_f = fields.Boolean('State')
    c_zip_f = fields.Boolean("Zipcode")
    c_country_f = fields.Boolean("Country")
    c_email_f = fields.Boolean("Email")
    c_tphone_f = fields.Boolean("Telephone")
    c_primary_tel_type_f = fields.Boolean("Telephone Type")

    c_alternate_communication_1_f = fields.Boolean("Other")
    c_alternate_commu_type_1_f = fields.Boolean("Other Type")

    c_alternate_communication_2_f = fields.Boolean("Other")
    c_alternate_commu_type_2_f = fields.Boolean("Other Type")

    # c_fax_f = fields.Boolean("Fax")
    # c_other_f = fields.Boolean("Other")

    c_website_f = fields.Boolean("Website")
    c_lang_f = fields.Boolean("Language")
    c_desc_f = fields.Boolean("Description") 


    @api.onchange('l_name_f',  'l_company_f',  'l_street_f',  'l_street2_f', 'l_city_f', 'l_state_f', 'l_zip_f', 'l_country_f')
    def onchange_flags1(self):
        if self.l_name_f:
            self.c_name_f = False     
        if self.l_company_f:
            self.c_company_f = False     
        if self.l_street_f:
            self.c_street_f = False      
        if self.l_street2_f:
            self.c_street2_f = False 
        if self.l_city_f:
            self.c_city_f = False     
        if self.l_state_f:
            self.c_state_f = False     
        if self.l_zip_f:
            self.c_zip_f = False      
        if self.l_country_f:
            self.c_country_f = False    
   

    @api.onchange('c_name_f', 'c_company_f', 'c_street_f', 'c_street2_f', 'c_city_f',  'c_state_f', 'c_zip_f',  'c_country_f')
    def onchange_flags12(self): 
        if self.c_name_f:
            self.l_name_f = False     
        if self.c_company_f:
            self.l_company_f = False     
        if self.c_street_f:
            self.l_street_f = False     
        if self.c_street2_f:
            self.l_street2_f = False  
        if self.c_city_f:
            self.l_city_f = False     
        if self.c_state_f:
            self.l_state_f = False     
        if self.c_zip_f:
            self.l_zip_f = False     
        if self.c_country_f:
            self.l_country_f = False 
   
    @api.onchange('l_email_f',  'l_tphone_f', 'l_alternate_communication_1_f','l_primary_tel_type_f', 'l_alternate_commu_type_1_f','l_alternate_commu_type_2_f','l_alternate_communication_2_f', 'l_website_f', 'l_lang_f', 'l_desc_f',)
    def onchange_flags3(self):
        if self.l_email_f:
            self.c_email_f = False     
        if self.l_tphone_f:
            self.c_tphone_f = False
        if self.l_primary_tel_type_f:
            self.c_primary_tel_type_f = False

        if self.l_alternate_communication_1_f:
            self.c_alternate_communication_1_f = False
        if self.l_alternate_commu_type_1_f:
            self.c_alternate_commu_type_1_f = False

        if self.l_alternate_communication_2_f:
            self.c_alternate_communication_2_f = False
        if self.l_alternate_commu_type_2_f:
            self.c_alternate_commu_type_2_f = False

        # if self.l_fax_f:
        #     self.c_fax_f = False      
        # if self.l_other_f:
        #     self.c_other_f = False

        if self.l_website_f:
            self.c_website_f = False     
        if self.l_lang_f:
            self.c_lang_f = False     
        if self.l_desc_f:
            self.c_desc_f = False       
   
    @api.onchange('c_email_f','c_primary_tel_type_f','c_alternate_communication_1_f','c_alternate_commu_type_1_f','c_alternate_communication_2_f','c_alternate_commu_type_2_f',  'c_tphone_f', 'c_website_f', 'c_lang_f',  'c_desc_f')
    def onchange_flags4(self):
        if self.c_email_f:
            self.l_email_f = False     
        if self.c_tphone_f:
            self.l_tphone_f = False
        if self.c_primary_tel_type_f:
            self.l_primary_tel_type_f = False
        if self.c_alternate_communication_1_f:
            self.l_alternate_communication_1_f = False
        if self.c_alternate_commu_type_1_f:
            self.l_alternate_commu_type_1_f = False
        if self.c_alternate_communication_2_f:
            self.l_alternate_communication_2_f = False
        if self.c_alternate_commu_type_2_f:
            self.l_alternate_commu_type_2_f = False
        if self.c_website_f:
            self.l_website_f = False    
        if self.c_lang_f:
            self.l_lang_f = False     
        if self.c_desc_f:
            self.l_desc_f = False       
   
          

    @api.multi
    def merge_link_customer(self):
        self.ensure_one()
        leads = self.lead_id 
        val_l = {}
        val_c = {}
        if self.c_name_f:
            val_l['contact_name'] = self.c_name 
        elif self.l_name_f :
            val_c['contact_name'] = self.l_name 
        if self.c_street_f:
            val_l['street'] = self.c_street 
        elif self.l_street_f :
            val_c['street'] = self.l_street
        if self.c_street2_f:
            val_l['street2'] = self.c_street2 
        elif self.l_street2_f :
            val_c['street2'] = self.l_street2
        if self.c_city_f:
            val_l['city'] = self.c_city 
        elif self.l_city_f :
            val_c['city'] = self.l_city
        if self.c_state_f:
            state_id = self.env['res.country.state'].search([('name','=',self.c_state)])
            val_l['state_id'] = state_id.id 
        elif self.l_state_f :
            state_id = self.env['res.country.state'].search([('name','=',self.l_state)])
            val_c['state_id'] = state_id.id
        if self.c_country_f:
            country_id = self.env['res.country'].search([('name','=',self.c_country)])
            val_l['country_id'] = country_id.id 
        elif self.l_country_f :
            country_id = self.env['res.country'].search([('name','=',self.l_country)])
            val_c['country_id'] = country_id.id
        if self.c_zip_f:
            val_l['zip'] = self.c_zip 
        elif self.l_zip_f :
            val_c['zip'] = self.l_zip
        if self.c_email_f:
            val_l['email_from'] = self.c_email 
        elif self.l_email_f :
            val_c['email'] = self.l_email
        if self.c_tphone_f:
            val_l['phone'] = self.c_tphone 
        elif self.l_tphone_f :
            val_c['phone'] = self.l_tphone

        if self.c_primary_tel_type_f:
            val_l['primary_tel_type'] = self.c_primary_tel_type.id
        elif self.l_primary_tel_type_f:
            val_c['primary_tel_type'] = self.l_primary_tel_type.id
        
        if self.c_alternate_communication_1_f:
            val_l['alternate_communication_1'] = self.c_alternate_communication_1

        elif self.l_alternate_communication_1_f:
            val_c['alternate_communication_1'] = self.l_alternate_communication_1
        
        if self.c_alternate_commu_type_1_f:
            val_l['alternate_commu_type_1'] = self.c_alternate_commu_type_1.id
        
        elif self.l_alternate_commu_type_1_f:
            val_c['alternate_commu_type_1'] = self.l_alternate_commu_type_1.id
        

        if self.c_alternate_communication_2_f:
            val_l['alternate_communication_2'] = self.c_alternate_communication_2
        elif self.l_alternate_communication_2_f:
            val_c['alternate_communication_2'] = self.l_alternate_communication_2

        if self.c_alternate_commu_type_2_f:
            val_l['alternate_commu_type_2'] = self.c_alternate_commu_type_2.id           
        elif self.l_alternate_commu_type_2_f:
            val_c['alternate_commu_type_2'] = self.l_alternate_commu_type_2.id

        if self.c_website_f:
            val_l['website'] = self.c_website 
        elif self.l_website_f :
            val_c['website'] = self.l_website
        if self.c_lang_f:
            val_l['lang'] = self.c_lang 
        elif self.l_lang_f :
            val_c['lang'] = self.l_lang
        if self.c_desc_f:
            desc_id = self.env['customer.description'].search([('name','=',self.c_desc)])
            val_l['desc'] = desc_id.id 
        elif self.l_desc_f:
            desc_id = self.env['customer.description'].search([('name','=',self.l_desc)])
            val_c['desc'] = desc_id.id
        val_c.update(val_l)
        res2 = leads.write(val_c)
        res1 = self.contact_id.write(val_c)
        leads.handle_partner_assignation(action='exist', partner_id=self.contact_id.id )
        leads.write({'active': True, 'state':'opport'})
        return True


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    assign_to = fields.Selection([('salesperson','Assign to SalesPerson'),('sale_team','Assign to Sales Team')],
                default='salesperson', string='Assign To')

    @api.onchange('assign_to')
    def onchange_lang(self):
        self.team_id = False
        self.user_id = False 

    @api.model
    def default_get(self, fields):
        result = super(Lead2OpportunityPartner, self).default_get(fields)
        if self._context.get('active_id'): 
            result['user_id'] = False
            result['team_id'] = False 
        if 'name' in fields:
            result['name'] = 'convert'
        result['action'] = 'exist'
        return result 

    @api.depends('action','user_id')
    def find_match(self):
        lead_id = self.env['crm.lead'].search([('id','=',self._context['active_id'])])
        contact_name = ''
        if lead_id.contact_name:
            contact_name += lead_id.contact_name
            if any([lead_id.company_name, lead_id.street, lead_id.street2, lead_id.city, lead_id.state_id.name, lead_id.zip]):
                contact_name += ', '
        if lead_id.company_name: 
            contact_name += lead_id.company_name
            if any([lead_id.street, lead_id.street2, lead_id.city, lead_id.state_id.name, lead_id.zip]):
                contact_name += ', '
        if lead_id.street: 
            contact_name += lead_id.street
            if any([lead_id.street2, lead_id.city, lead_id.state_id.name, lead_id.zip]):
                contact_name += ', '
        if lead_id.street2: 
            contact_name += lead_id.street2
            if any([lead_id.city, lead_id.state_id.name, lead_id.zip]):
                contact_name += ', '
        if lead_id.city: 
            contact_name += lead_id.city
            if any([lead_id.state_id.name, lead_id.zip]):
                contact_name += ', '
        if lead_id.state_id.name: 
            contact_name += lead_id.state_id.name
            if lead_id.zip:
                contact_name += ', '
        if lead_id.zip: 
            contact_name += lead_id.zip
        self.found_customer_wizard = str(contact_name)
    
    action = fields.Selection([
        ('exist','Merge with this existing contact'),
        ('create_contact', 'Create new contact for this account'),
        ('create', 'Create new account')], default='exist')
    get_contact_name = fields.Char('Contact', compute='find_contact_details')
    get_company_name = fields.Char('Company', compute='find_contact_details')
    get_street = fields.Char('Address', compute='find_complete_address')
    get_email = fields.Char('Email', compute='find_contact_details')
    get_phone = fields.Char('telephone', compute='find_contact_details')
    partner_wizard = fields.Char(compute='find_fields_value')
    opportunity_wizard =fields.Char(compute='find_fields_value',  readonly=False)
    contact_wizard =fields.Char(compute='find_fields_value')
    contact_name = fields.Char('Contact')
    found_customer_wizard = fields.Char(compute='find_match', string='Lead name and address')
    contact_id = fields.Many2one('res.partner', string='Contacts')

    # lead_partner_line_ids = fields.One2many('crm.lead.partner.tree' , 'lead_partner_line_id',
    #  help="All possible merged contact list appears here")
    # check_id = fields.Many2one('res.partner',  string="Selected")


    # @api.onchange('lead_partner_line_ids')
    # def find_checked_value(self):
    #     selected = None
            
    #     for line in self.lead_partner_line_ids:
    #         if self.check_id:
    #             for rec in self.lead_partner_line_ids:
    #                 if self.check_id == line.partner_id:
    #                     rec.is_merge = False
    #                     self.check_id = False
    #         elif line.is_merge: 
    #             self.check_id = line.partner_id.id 
    #             break 
    #     if selected:
    #         for line2 in self.lead_partner_line_ids:
    #             if selected.partner_id == line2.partner_id:
    #                 continue
    #             else:
    #                 line2.is_merge = False
    
    #..............COPY FIELDS OF LEAD ACTIVE ID IN ACCEPT WIZARD..........

    # @api.depends('action','user_id')
    # def find_contact_details(self):
    #     contact = self.env['crm.lead'].search([('id','=',self._context['active_id'])])
    #     if contact:
    #         self.get_contact_name = contact.contact_name
    #     if contact:
    #         self.get_company_name = contact.company_name
    #     if contact:
    #         self.get_email = contact.email_from
    #     if contact:
    #         self.get_phone = contact.get_phone

    # @api.depends('action','user_id')
    # def find_lead_address(self):
    #     lead_id = self.env['crm.lead'].search([('id','=',self._context['active_id'])])
    #     contact_name = ''
    #     if lead_id.street: 
    #         contact_name += ', ' + lead_id.street
    #     if lead_id.street2: 
    #         contact_name += ' ' + lead_id.street2
    #     if lead_id.city: 
    #         contact_name += ', ' + lead_id.city
    #     if lead_id.state_id.name: 
    #         contact_name += ' ' + lead_id.state_id.name
    #     if lead_id.zip: 
    #         contact_name += ' ' + lead_id.zip
    #     self.get_street = str(contact_name)
    #     return contact_name

    # @api.depends('action','user_id')
    # def find_complete_address(self):
    #     temp = self.env['crm.lead'].search([('id','=',self._context['active_id'])])
    #     first_part = (str(temp.street) +" "+ str(temp.street2)).split()
    #     first_part_str = ""
    #     for rec in first_part:
    #         if rec != 'False':
    #             first_part_str = first_part_str + " " + rec
    #     second_part = (str(temp.city) + " " + str(temp.state_id.code) + " " + str(temp.zip)).split()
    #     second_part_str = ""
    #     for rec in second_part:
    #         if rec != 'False':
    #             second_part_str = second_part_str + " " + rec
    #     complete_address_str = '\n'.join([first_part_str, second_part_str])
    #     if len(first_part_str) > 0:
    #         self.get_street = complete_address_str
    #     else:
    #         self.get_street = second_part_str
    
    #COPY FIELD VALUE FROM LEAD VIEW TO LEAD WIZARD VIEW
    @api.depends('user_id')
    def find_fields_value(self):
        partner_name = self.env['crm.lead'].search([('id','=',self._context['active_id'])])
        if partner_name:
            self.contact_wizard = partner_name.contact_name
            self.partner_wizard= partner_name.partner_id.name
            self.opportunity_wizard= partner_name.name


    #UPDATE OPPORTUNITY FIELD FROM LEAD WIZARD VIEW TO LEAD VIEW
    
    @api.onchange('opportunity_wizard')
    def _get_opportunity_name(self):
        vals = {}
        partner_name = self.env['crm.lead'].search([('id','=',self._context['active_id'])])
        if self.opportunity_wizard != partner_name.name:
            vals['name'] = self.opportunity_wizard
            partner_name.write(vals)
    
    # @api.onchange('action')
    # def onchange_action(self):
    #     add_line = []
    #     self.lead_partner_line_ids = False
    #     if self.action  == 'exist':
           
    #         for id in self._find_matching_contact():
    #             value = {'partner_id':id}
    #             add_line.append((0,0,value))
    #         if add_line:
    #             self.lead_partner_line_ids = add_line
    #     elif self.action  ==  'create_contact':
           
    #         for id in self._find_matching_partner():
    #             value = {'partner_id':id}
    #             add_line.append((0,0,value))
    #         if add_line:
    #             self.lead_partner_line_ids = add_line
    #     else:
    #         self.partner_id = False

    @api.onchange('action')
    def onchange_action(self):
        if self.action in ['exist','create_contact']:
            self.partner_id = self._find_matching_partner()
            self.contact_id = self._find_matching_contact()
        else:
            self.partner_id = False


    @api.multi
    def action_create_customer(self):
        self.ensure_one()
        partner_env = self.env['res.partner']
        leads = self.env['crm.lead'].browse(self._context.get('active_ids', []))
        if self.action == 'exist':
            contact_id = self.contact_id
            text = "Message! No Changes found to update"
            vals = {}
            flag_diff = False
            vals['lead_id']= leads.id
            vals['contact_id']= contact_id.id
            vals['c_name'] = contact_id.name
            vals['c_company'] = contact_id.parent_id.name
            vals['c_street'] = contact_id.street
            vals['c_street2'] = contact_id.street2
            vals['c_city'] = contact_id.city
            vals['c_state'] = contact_id.state_id.name
            vals['c_zip'] = contact_id.zip
            vals['c_country'] = contact_id.country_id.name
            vals['c_email'] = contact_id.email
            vals['c_tphone'] = contact_id.phone
            vals['c_primary_tel_type'] = contact_id.primary_tel_type.id
            vals['c_alternate_communication_1'] = contact_id.alternate_communication_1
            vals['c_alternate_commu_type_1'] = contact_id.alternate_commu_type_1.id
            vals['c_alternate_communication_2'] = contact_id.alternate_communication_2
            vals['c_alternate_commu_type_2'] = contact_id.alternate_commu_type_2.id
            vals['c_website'] = contact_id.website
            vals['c_lang'] = contact_id.lang
            vals['c_desc'] = contact_id.desc.name


            vals['l_name'] = leads.contact_name
            vals['l_company'] = leads.company_name
            vals['l_street'] = leads.street
            vals['l_street2'] = leads.street2
            vals['l_city'] = leads.city
            vals['l_state'] = leads.state_id.name
            vals['l_zip'] = leads.zip
            vals['l_country'] = leads.country_id.name
            vals['l_email'] = leads.email_from
            vals['l_tphone'] = leads.phone
            vals['l_primary_tel_type'] = leads.primary_tel_type.id
            vals['l_alternate_communication_1'] = leads.alternate_communication_1
            vals['l_alternate_commu_type_1'] = leads.alternate_commu_type_1.id
            vals['l_alternate_communication_2'] = leads.alternate_communication_2
            vals['l_alternate_commu_type_2'] = leads.alternate_commu_type_2.id
            vals['l_website'] = leads.website
            vals['l_lang'] = leads.lang
            vals['l_desc'] = leads.desc.name

            if contact_id.name == leads.contact_name:
                vals['c_name_f'] = True
                vals['name_f'] = True
            else:
                vals['l_name_f'] = True
                flag_diff = True

            if contact_id.parent_id.name == leads.company_name:
                vals['c_company_f'] = True
                vals['company_f'] = True
            else:
                vals['l_company_f'] = True
                flag_diff = True
                
            if contact_id.street == leads.street:
                vals['c_street_f'] = True
                vals['street_f'] = True
            else:
                vals['l_street_f'] = True
                flag_diff = True
                
            if contact_id.street2 == leads.street2:
                vals['c_street2_f'] = True
                vals['street2_f'] = True
            else:
                vals['l_street2_f'] = True
                flag_diff = True
                
            if contact_id.city == leads.city:
                vals['c_city_f'] = True
                vals['city_f'] = True
            else:
                vals['l_city_f'] = True
                flag_diff = True
                
            if contact_id.state_id.name == leads.state_id.name:
                vals['c_state_f'] = True
                vals['state_f'] = True
            else:
                vals['l_state_f'] = True
                flag_diff = True
                
            if contact_id.zip == leads.zip:
                vals['c_zip_f'] = True
                vals['zip_f'] = True
            else:
                vals['l_zip_f'] = True
                flag_diff = True
                
            if contact_id.country_id.name == leads.country_id.name:
                vals['c_country_f'] = True
                vals['country_f'] = True
            else:
                vals['l_country_f'] = True
                flag_diff = True
                
            if contact_id.email == leads.email_from:
                vals['c_email_f'] = True
                vals['email_f'] = True
            else:
                vals['l_email_f'] = True
                flag_diff = True
                
            if contact_id.phone == leads.phone:
                vals['c_tphone_f'] = True
                vals['tphone_f'] = True
            else:
                vals['l_tphone_f'] = True
                flag_diff = True

            if contact_id.primary_tel_type.name == leads.primary_tel_type.name:
                vals['c_primary_tel_type_f'] = True
                vals['primary_tel_type_f'] = True
            else:
                vals['l_primary_tel_type_f'] = True
                flag_diff = True

            if contact_id.alternate_communication_1 == leads.alternate_communication_1:
                vals['c_alternate_communication_1_f'] = True
                vals['alternate_communication_1_f'] = True
            else:
                vals['l_alternate_communication_1_f'] = True
                flag_diff = True

            if contact_id.alternate_commu_type_1.name == leads.alternate_commu_type_1.name:
                vals['c_alternate_commu_type_1_f'] = True
                vals['alternate_commu_type_1_f'] = True
            else:
                vals['l_alternate_commu_type_1_f'] = True
                flag_diff = True

            if contact_id.alternate_communication_2 == leads.alternate_communication_2:
                vals['c_alternate_communication_2_f'] = True
                vals['alternate_communication_2_f'] = True
            else:
                vals['l_alternate_communication_2_f'] = True
                flag_diff = True

            if contact_id.alternate_commu_type_2.name == leads.alternate_commu_type_2.name:
                vals['c_alternate_commu_type_2_f'] = True
                vals['alternate_commu_type_2_f'] = True
            else:
                vals['l_alternate_commu_type_2_f'] = True
                flag_diff = True
                
            if contact_id.website == leads.website:
                vals['c_website_f'] = True
                vals['website_f'] = True
            else:
                vals['l_website_f'] = True
                flag_diff = True
                
            if contact_id.lang == leads.lang:
                vals['c_lang_f'] = True
                vals['lang_f'] = True
            else:
                vals['l_lang_f'] = True
                flag_diff = True
                
            if contact_id.desc.id == leads.desc.id:
                vals['c_desc_f'] = True
                vals['desc_f'] = True
            else:
                vals['l_desc_f'] = True
                flag_diff = True
            #vals['found_customer'] = str(self.found_customer)        
            if not flag_diff:
                leads.handle_partner_assignation(action='exist', partner_id=self.contact_id.id )
                leads.write({'active': True, 'state':'opport'}) 
                return True
            partial = self.env['lead.merge.partner'].create(vals) 
            return {'name': ("Merge Lead with Contact"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'lead.merge.partner',
                'view_id': False,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                }
        if self.action == 'create_contact':
            text = "Message! No Changes found to update"
            vals = {}
            vals = {
                'name': leads.contact_name,
                'comp_name':leads.company_name,
                'street':leads.street,
                'street2':leads.street2,
                'city':leads.city,
                'desc':leads.desc.id,
                'email':leads.email_from,
                'zip':leads.zip,
                'phone':leads.phone,
                'alternate_communication_1':leads.alternate_communication_1,
                'alternate_communication_2':leads.alternate_communication_2,
                'website':leads.website,
                'lang':leads.lang,
                'type':'other',
                'type_extend':'contact',
                'parent_id':self.partner_id.id,
                'supplier': False,
                'customer': False,
                'active': True
                  }
            if leads.primary_tel_type:
                vals['primary_tel_type'] = leads.primary_tel_type.id,
            if leads.alternate_commu_type_1:
                vals['alternate_commu_type_1'] = leads.alternate_commu_type_1.id
            if leads.alternate_commu_type_2:
                vals['alternate_commu_type_2'] = leads.alternate_commu_type_2.id
            if leads.state_id:
                vals['state_id'] = leads.state_id.id
            if leads.country_id:
                vals['country_id'] = leads.country_id.id
            res = partner_env.create(vals)
            leads.handle_partner_assignation(action=self.action, partner_id=res.id)
            leads.write({'active': True, 'state':'opport'})
            return True
        leads.handle_partner_assignation(action=self.action, partner_id=self.partner_id.id if self.action == 'exist' else False)
        leads.write({'active': True, 'state':'opport'})
        return {'type': 'ir.actions.act_window_close'}   

# class LeadMergePartnerTree(models.TransientModel):
#     _name = 'crm.lead.partner.tree'

#     lead_partner_line_id = fields.Many2one('crm.lead2opportunity.partner')
#     partner_id = fields.Many2one('res.partner')
#     is_merge = fields.Boolean(string=' ')
#     contact_name = fields.Char(related='partner_id.name', string='Contact')
#     account_name = fields.Char(related='partner_id.parent_id.name', string='Account')
#     get_address = fields.Char(related='partner_id.street',string='Address')
#     city = fields.Char(related='partner_id.city', string='City')
#     state = fields.Char(related='partner_id.state_id.code', string='State')
#     zip_code = fields.Char(related='partner_id.zip', string='Zipcode')
#     email_from = fields.Char(related='partner_id.email', string='Email')
#     phone_no = fields.Char(related='partner_id.phone', string='Telephone')