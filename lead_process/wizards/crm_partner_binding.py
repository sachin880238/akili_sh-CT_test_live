# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
    
class PartnerBinding(models.TransientModel):
    _inherit = 'crm.partner.binding'

    action = fields.Selection([
        ('exist', 'Link to an existing customer'),
        ('create', 'Create a new customer'),
    ])

    @api.model
    def _find_matching_partner(self):
        """
        Overwrite the functionality to search for customer=True record only
        """
        # active model has to be a lead
        if self._context.get('active_model') != 'crm.lead' or not self._context.get('active_id'):
            return False

        lead = self.env['crm.lead'].browse(self._context.get('active_id'))

        # find the best matching partner for the active model
        Partner = self.env['res.partner']
        domain = [('customer','=',True)]
        if lead.partner_id:  # a partner is set already
            return lead.partner_id.commercial_partner_id.id

        if lead.email_from:  # search through the existing partners based on the lead's email
            partner = Partner.search(domain+[('email', '=', lead.email_from)], limit=1)
            return partner.id

        if lead.partner_name:  # search through the existing partners based on the lead's partner or contact name
            partner = Partner.search(domain+[('name', 'ilike', '%' + lead.partner_name + '%')], limit=1)
            return partner.id

        if lead.contact_name:
            partner = Partner.search(domain+[('name', 'ilike', '%' + lead.contact_name+'%')], limit=1)
            return partner.id


        # if lead.email_from:  # search through the existing partners based on the lead's email
        #     partner = Partner.search(domain+[('email', '=', lead.email_from)])
        #     return partner.ids

        # if lead.partner_name:  # search through the existing partners based on the lead's partner or contact name
        #     partner = Partner.search(domain+[('name', 'ilike', '%' + lead.partner_name + '%')])
        #     return partner.ids

        # if lead.contact_name:
        #     partner = Partner.search(domain+[('name', 'ilike', '%' + lead.contact_name+'%')])
        #     return partner.ids

        return False


    @api.model
    def _find_matching_contact(self):
        """ Try to find a matching partner regarding the active model data, like
            the customer's name, email, phone number, etc.
            :return int partner_id if any, False otherwise
        """
        # active model has to be a lead
        if self._context.get('active_model') != 'crm.lead' or not self._context.get('active_id'):
            return False

        lead = self.env['crm.lead'].browse(self._context.get('active_id'))

        # find the best matching partner for the active model
        Partner = self.env['res.partner']

        if lead.contact_name:
            partner = Partner.search([('name', 'ilike', '%' + lead.contact_name+'%')], limit=1)
            return partner.id
        return False
