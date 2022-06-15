from odoo import api, fields, models, _
import logging
import datetime
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import base64, urllib.request
from odoo.exceptions import UserError
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = 'res.partner'

    display_name = fields.Char(compute='_compute_display_name', store=False, index=True)
    comp_name = fields.Char(string='Company')
    property_delivery_carrier_id = fields.Many2one('delivery.carrier', company_dependent=True, string="Delivery Method", help="This delivery method will be used when invoicing from picking.")

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name', 'comp_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=False)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)
 
    @api.multi
    def name_get(self):
        res = []
        if self._context.get('show_custom_address') or self._context.get('from_account'):
            for partner in self:
                name = partner.name or ''
                if partner.company_name or partner.parent_id:
                    if not name and partner.type in ['invoice', 'delivery', 'other', 'purchase']:
                        name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
                    if not partner.is_company:
                        name = "%s, %s" % (name, partner.commercial_company_name or partner.parent_id.name,)
                args = {
                    'name': name,
                    'state_code': partner.state_id.code or '',
                    'state_name': partner.state_id.name or '',
                    'country_code': partner.country_id.code or '',
                    'country_name': partner.country_id.name or '',
                    'company_name': partner.commercial_company_name or '',
                }
                for field in partner._address_fields():
                    args[field] = getattr(partner, field) or ''
                if args.get('street', '') != '' or args.get('street2', '') != '':
                    name += ', %(street)s %(street2)s' % (args)
                if args.get('city', '') != '' or args.get('state_code', '') != '' or args.get('zip', '') != '':
                    name += ', %(city)s %(state_code)s %(zip)s' % (args)
                if partner.parent_id:
                    res.append((partner.id, name))
                elif partner.company_address_id:
                    res.append((partner.id, name))
                else:
                    res.append((partner.id, partner.name))
            return res

        else:
            for partner in self:
                if self._context.get('address_view', False):
                    if partner.comp_name and partner.name:
                        name = partner.name + "," + " " +partner.comp_name
                        res.append((partner.id, name))
                    elif partner.comp_name:
                        res.append((partner.id, partner.comp_name))
                    elif partner.name:
                        res.append((partner.id, partner.name))
                else:
                    return super(ResPartner, self).name_get()
            return res

    @api.model
    def get_text_format(self,ids=[]):
        data=[]
        for rec in ids:
            partner_id=self.env['res.partner'].search([('id','=',rec)])
            string_format=partner_id.name
            if partner_id.company_id:
                string_format=string_format+"<div>"+partner_id.company_id.name
            if partner_id.street:
                string_format=string_format+"</div><div>"+partner_id.street
            if partner_id.city:
                string_format=string_format+'</div><div>'+partner_id.city
            if not partner_id.city and partner_id.state_id:
                string_format=string_format+'</div><div>'+partner_id.state_id.name
            if partner_id.city and partner_id.state_id:
                string_format=string_format+' '+partner_id.state_id.name
            if not partner_id.city and not partner_id.state_id and  partner_id.zip:
                string_format=string_format+'</div><div>'+partner_id.zip
            if partner_id.city or partner_id.state_id and partner_id.zip:
                string_format=string_format+' '+partner_id.zip
            if partner_id.country_id:
                string_format=string_format+'</div><div>'+partner_id.country_id.name
            else:
                string_format=string_format+'</div>'
            data.append([partner_id.id,string_format])    
        return data


    

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = [('name', operator, name)]
        partner_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(partner_ids).sudo(name_get_uid))
