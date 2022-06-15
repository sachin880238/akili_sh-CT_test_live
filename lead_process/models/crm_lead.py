from odoo import models, fields, tools, api
from datetime import datetime, timedelta, date
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, ValidationError
from . import crm_stage


@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _order = "sequence"

    sequence = fields.Integer(help="Gives the sequence order when displaying a list of product categories.")
    name =fields.Char(string='Opportunity', required=0)
    company_name = fields.Char(string="Company")
    contact_name = fields.Char(string='Contact')
    lead_name = fields.Char(string='Lead Name' ,compute="_get_lead_name")
    opp_date = fields.Date(string='Date Created')
    campaign = fields.Char(string='Campaign')
    medium = fields.Char(string='Medium')
    source = fields.Char(string='Source')
    referred_by = fields.Char(string='Referred By')
    partner_id = fields.Many2one(string="Account")
    commercial_partner_id = fields.Many2one('res.partner', string='Customer', readonly=True,)
    active = fields.Boolean(copy=False)
    state = fields.Selection(
                [('account', 'REVIEW'),
                 ('delay','HOLD'),
                 ('opport', 'ASSIGN'),
                 ('done', 'OPPORTUNITY '),
                 ('close','CLOSED'),
                 ], default='account',string='Stage')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    status = fields.Char(compute="get_lead_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    street3 = fields.Char()
    desc = fields.Many2one('customer.description', "Description")
    fax = fields.Char(
        string='Fax',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=True
    )
    @api.depends('parent_state')
    def get_lead_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    @api.depends('stage_id','planned_revenue','probability')
    def get_current_value(self):
        for rec in self:
            if rec.planned_revenue and rec.probability:
                rec.current_planned_revenue = rec.planned_revenue * rec.probability / 100

    get_website = fields.Char("Website",compute='get_comm_attributes')   
    lead_team = fields.Many2one('crm.team', string='Lead Team')
    lang = fields.Selection(_lang_get, string='Language', default=lambda self: self.env.lang,
                            help="If the selected language is loaded in the system, all documents related to "
                                 "this contact will be printed in this language. If not, it will be English.")
    priority = fields.Selection(crm_stage.AVAILABLE_PRIORITIES, string='Rating', index=True, default=crm_stage.AVAILABLE_PRIORITIES[0][0])
    partner_name = fields.Char("Customer Name", index=True, help='The name of the future partner company that will be created while converting the lead into opportunity')
    user_id = fields.Many2one('res.users', string='Salesperson')
    team_id = fields.Many2one('crm.team', string='Sales Team')
    created_date = fields.Datetime('Created', default=fields.Datetime.now, readonly=True)
    quotation_warning = fields.Text('Quotation Warning')
    opportunity_notes = fields.Text('Opportunity Notes')
    scoring_rules = fields.Text('Scoring Rules')
    lang = fields.Selection(string='Language', selection='_get_lang')
    image = fields.Binary("Image", attachment=True)
    icon_letters = fields.Char("Icon", size=2)
    alternate_communication_1 = fields.Char()
    get_alternate_communication_1 = fields.Char(compute='get_comm_attributes')
    alternate_communication_2 = fields.Char()
    get_alternate_communication_2 = fields.Char(compute='get_comm_attributes')
    get_phone = fields.Char(compute='get_comm_attributes')
    primary_tel_type = fields.Many2one('communication.type')
    alternate_commu_type_1 = fields.Many2one('communication.type')
    alternate_commu_type_2 = fields.Many2one('communication.type')
    category_ids = fields.Many2many('crm.lead.tag', 'crm_lead_tag_rel', 'lead_id', 'tag_id', string='Tags')
    probability = fields.Integer(group_operator="avg", default=lambda self: self._default_probability())
    planned_revenue = fields.Monetary(currency_field='company_currency', track_visibility='always')
    current_planned_revenue = fields.Monetary(string="Current Value", compute='get_current_value', store=True, currency_field='company_currency')
    state_code = fields.Char("State",related="state_id.code")
    complete_address = fields.Text(compute="get_complete_address")
    quote_count = fields.Integer('Quotations')

    @api.multi
    def get_quotation(self):
        action = self.env.ref('account_contacts.customer_quotations_list').read()[0]
        return action

    @api.depends('lead_team')
    def find_lead_team_member(self):
        for rec in self:
            if rec.lead_team:
                if rec.lead_team.user_ids:
                    for line in rec.lead_team.user_ids:
                        if line.id == rec.env.user.id:
                            rec.is_lead_team_member = True
                            
    is_lead_team_member = fields.Boolean(compute='find_lead_team_member')

    def copy(self, default=None):
        if default is None:
            default = {}
        if self.state == 'done':
            if self.name:
                default['name'] = _("%s (Copy)") % self.name            
        elif self.contact_name:
            default['contact_name'] = _("%s (Copy)") % self.contact_name
        elif self.company_name:
            default['company_name'] = _("%s (Copy)") % self.company_name
        elif self.email_from:
            default['email_from'] = _("%s (Copy)") % self.email_from
        elif self.phone:
            default['phone'] = _("%s (Copy)") % self.phone
        else:
            default['website'] = _("%s (Copy)") % self.website
        return super(CrmLead, self).copy(default=default)

    @api.depends('street','street2','street3','city','state_id','zip','country_id')
    def get_complete_address(self):
        complete_address = ''
        if self._context.get('default_type') == 'opportunity' or self.state == 'done': 
            if self.contact_name:
                complete_address += self.contact_name
                if any([self.company_name,self.street2,self.street3,self.city,self.state_id,self.zip,self.country_id]):
                    complete_address += '\n' 
            if self.company_name:
                complete_address += self.company_name
                if any([self.street2,self.street3,self.city,self.state_id,self.zip,self.country_id]):
                    complete_address += '\n'
        if self.street:
            complete_address += self.street
            if any([self.street2,self.street3,self.city,self.state_id,self.zip,self.country_id]):
                complete_address += '\n'
        if self.street2: 
            complete_address += self.street2
            if any([self.street3,self.city, self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.street3: 
            complete_address += self.street3
            if any([self.city, self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.city and self.state_id and self.zip : 
            complete_address += self.city + ' ' + self.state_id.code + ' ' + self.zip
            if any([self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.city and self.state_id and not self.zip : 
            complete_address += self.city + ' ' + self.state_id.code
            if any([self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.city and self.zip and not self.state_id : 
            complete_address += self.city + ' ' + self.zip
            if any([self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.state_id and self.zip and not self.city : 
            complete_address += self.state_id.code + ' ' + self.zip
            if any([self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.city and not self.state_id and not self.zip: 
            complete_address += self.city
            if any([self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.state_id and not self.city and not self.zip: 
            complete_address += self.state_id.code
            if any([self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.zip and not self.city and not self.state_id: 
            complete_address += self.zip
            if any([self.state_id, self.zip ,self.phone, self.country_id]):
                complete_address += '\n'
        if self.country_id:
            complete_address += self.country_id.name

        self.complete_address = str(complete_address)

    @api.multi
    def get_comm_attributes(self):
        for rec in self:
            if rec.phone:
                if rec.primary_tel_type:
                    telephone = rec.phone + " ("+ rec.primary_tel_type.name + ")"
                    rec.get_phone = str(telephone)
                else:
                    rec.get_phone = rec.phone
            if rec.alternate_communication_1:
                if rec.alternate_commu_type_1:
                    other1 = rec.alternate_communication_1 + " ("+ rec.alternate_commu_type_1.name + ")"
                    rec.get_alternate_communication_1 =  str(other1)
                else:
                    rec.get_alternate_communication_1 =  rec.alternate_communication_1 
            if rec.alternate_communication_2:
                if rec.alternate_commu_type_2:
                    other2 =  rec.alternate_communication_2 + " ("+ rec.alternate_commu_type_2.name + ")"
                    rec.get_alternate_communication_2 = str(other2)
                else:
                    rec.get_alternate_communication_2 = rec.alternate_communication_2
            if rec.website:
                rec.get_website = rec.website
            else:
                rec.get_website = " "
    
    @api.model
    def _get_lang(self):
        return self.env['res.lang'].get_installed()
    
    @api.multi
    def hold_lead(self):
        self.write({'state':'delay'}) #Hold lead 
        return True
    
    @api.multi
    def open_lead(self):
        if self.partner_id:
            self.write({'state':'opport'}) #Open lead
        else:
            self.write({'state':'account'}) 
        return True

    @api.multi
    def return_to_review(self):
        self.write({'state':'account'}) #Lead return to review state after hold state 
        return True

    @api.multi
    def return_to_assign(self):
        self.write({'state':'opport'}) #Lead return to assign after accepted
        return True

    @api.multi
    def close_active_lead(self):
        self.write({'state':'close'}) #Close the lead
        return True

    @api.multi
    def activate_lead_active(self):
        if self.commercial_partner_id:
            self.write({'active': True, 'state':'opport'})  #Activate the lead
        else:
            self.write({'active': True, 'state':'account'})  #Activate the lead
        return True

    def _get_lead_name(self):
        if self.state == 'done':
            if self.name:
                self.lead_name = self.name            
        elif self.contact_name:
            self.lead_name=self.contact_name
        elif self.company_name:
            self.lead_name=self.company_name
        elif self.email_from:
            self.lead_name=self.email_from
        elif self.phone:
            self.lead_name=self.phone
        else:
            self.lead_name=self.website

    @api.multi
    def name_get(self):
        result = []
        if self._context.get('default_type') == 'lead':    
            for rec in self:
                if rec.contact_name:
                    result.append((rec.id,'%s' %(rec.contact_name)))
                    return result
                elif rec.company_name:
                    result.append((rec.id,'%s' %(rec.company_name)))
                    return result
                else:
                    result.append((rec.id,'%s' %(rec.email_from)))
                    return result

        elif self._context.get('default_type') == 'opportunity':
            for rec in self:
                if rec.name:
                    result.append((rec.id,'%s' %(rec.name)))
                    return result

        else:
            for rec in self:
                if rec.contact_name:
                    result.append((rec.id,'%s' %(rec.contact_name)))
                    return result
                elif rec.company_name:
                    result.append((rec.id,'%s' %(rec.company_name)))
                    return result
                else:
                    result.append((rec.id,'%s' %(rec.email_from)))
                    return result

    @api.model
    def create(self, vals):
        if all([not vals.get('company_name') and not vals.get('contact_name') and not vals.get('email_from')]):
            raise ValidationError("Please fill any one of the following: \n 1. Contact \n 2. Company \n 3. Email")
        else:
            context = dict(self._context or {})
            if not self._context.get('default_type'):
                context['default_type'] = 'opportunity'
                vals['state'] = 'done'
            if vals.get('team_id') and not self._context.get('default_team_id'):
                context['default_team_id'] = vals.get('team_id')
            if vals.get('user_id') and 'date_open' not in vals:
                vals['date_open'] = fields.Datetime.now()

            partner_id = vals.get('partner_id') or context.get('default_partner_id')
            onchange_values = self._onchange_partner_id_values(partner_id)
            onchange_values.update(vals)  # we don't want to overwrite any existing key
            vals = onchange_values

            # context: no_log, because subtype already handle this
            return super(CrmLead, self.with_context(context, mail_create_nolog=True)).create(vals)

    @api.multi
    def write(self, vals):
        result = super(CrmLead, self).write(vals)
        if all([not self.company_name and not self.contact_name and not self.email_from]):
            raise ValidationError("Please fill any one of the following: \n 1. Contact \n 2. Company \n 3. Email")
        return result


    @api.multi
    def create_partner_lead(self):
        return True

    @api.multi
    def _create_lead_partner_data(self, name, is_company, parent_id=False,company_type=None):
        """ extract data from lead to create a partner
            :param name : furtur name of the partner
            :param is_company : True if the partner is a company
            :param parent_id : id of the parent partner (False if no parent)
            :returns res.partner record
        """
        vals = {
            'company_type' : company_type,
            'name': name,
            'street': self.street,
            'street2': self.street2,
            'street3': self.street3,
            'city': self.city,
            'state_id': self.state_id.id,
            'zip': self.zip,
            'country_id': self.country_id.id,
            'desc': self.desc.id,
            'email': self.email_from,
            'phone': self.phone,
            'primary_tel_type':self.primary_tel_type.id,
            'alternate_communication_1':self.alternate_communication_1,
            'alternate_commu_type_1':self.alternate_commu_type_1.id,
            'alternate_communication_2':self.alternate_communication_2,
            'alternate_commu_type_2':self.alternate_commu_type_2.id,
            'website': self.website,
            'lang':self.lang,
            'is_company': is_company,
            'user_id': self.env.context.get('default_user_id') or self.user_id.id,
            'team_id': self.team_id.id,
            'campaign_id': self.campaign_id.name,
            'medium_id': self.medium_id.name,
            'source_id': self.source_id.name,
            'referred': self.referred,
        }
        return vals

    @api.multi
    def _create_lead_partner(self):
        """ Create a partner from lead data
            :returns res.partner record
        """
        partner = self.env['res.partner']
        contact_name = self.contact_name
        contact_type = None
        if not contact_name:

            #contact_name = Partner._parse_partner_name(self.email_from)[0] if self.email_from else False
            contact_name = self.company_name
            contact_type = 'company'

        if self.partner_name:
            partner_company = partner.create(self._create_lead_partner_data(self.partner_name, True))
        elif self.partner_id:
            partner_company = self.partner_id
        else:
            partner_company = None

        if contact_name:
            return partner.create(self._create_lead_partner_data(contact_name, False, partner_company.id if partner_company else False, contact_type))

        if partner_company:
            return partner_company
        return partner.create(self._create_lead_partner_data(self.name, False))

    @api.multi
    def handle_partner_assignation(self, action='create', partner_id=False):
        for lead in self:
            partner_company = False
            if action == 'create':
                lead.partner_id = False
                partner = lead._create_lead_partner()
                partner_id = partner.id
            if action == 'exist':
                contact_name = self.contact_name
                if not contact_name:
                    contact_name = self.env['res.partner']._parse_partner_name(self.email_from)[0] if self.email_from else False
                partner = self.env['res.partner'].search([('id','=', partner_id)])
                partner_id = partner_id
            if partner_id:
                # CT customized values are updated while creating partner from lead
                partner_vals = {
                    'campaign_id': lead.campaign_id.id,
                    'medium_id': lead.medium_id.id,
                    'source_id': lead.source_id.id,
                    'referred': lead.referred,
                }
                if lead.partner_id.parent_id:
                    partner_vals.update({
                        'company_name': lead.commercial_partner_id.company_type == 'company' and lead.commercial_partner_id.name or lead.company_name,
                        'parent_id': lead.partner_id.parent_id.id,
                        'customer': False,
                        'supplier': False,
                    })
                lead.partner_id.write(partner_vals)
        return super(CrmLead,self).handle_partner_assignation(action=action,partner_id=partner_id)

    @api.multi
    def redirect_opportunity_view(self):
        self.write({'state':'done'})
        return True
