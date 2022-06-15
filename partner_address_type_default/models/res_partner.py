# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOSC, Pedro M. Baeza, Sodexis, OdooMRP team
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_address = fields.Boolean('Default')

    @api.model
    def create(self, values):
        partner = super(ResPartner, self).create(values)
        if ('default_address' in values and values.get('default_address') and
                partner.parent_id and partner.type in ('invoice', 'delivery','other','purchase')):
            cond = [('parent_id', '=', partner.parent_id.id),
                    ('id', '!=', partner.id),
                    ('type', '=', partner.type)]
            partners = self.search(cond)
            if partners:
                partners.write({'default_address': False})
        return partner

    @api.one
    def write(self, values):
        result = super(ResPartner, self).write(values)
        if ('default_address' in values and values.get('default_address') and
                self.parent_id and self.type in ('invoice', 'delivery','other','purchase')):
            cond = [('parent_id', '=', self.parent_id.id),
                    ('id', '!=', self.id),
                    ('type', '=', self.type)]
            partners = self.search(cond)
            if partners:
                partners.write({'default_address': False})
        return result
