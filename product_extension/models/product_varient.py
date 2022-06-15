# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    sequence = fields.Integer(string='Sequence')
    before = fields.Char(string='Before')  
    after = fields.Char(string='After')
    uom_ids=fields.Many2one('uom.uom',string='Unit of measure')   

    @api.model
    def create(self, vals):
        if not vals['value_ids']: 
            raise UserError(_('Attriute value is required to create Product Template.'))
        # if len(vals['value_ids'][0][2]) <= 1:
        #     raise UserError( _('Atleast two values are required for each Attribute'))
        attr_line = self.search([('product_tmpl_id','=',vals['product_tmpl_id'])])
        vals['sequence'] = len(attr_line) +1 
        res = super(ProductTemplateAttributeLine, self).create(vals)
        return res

