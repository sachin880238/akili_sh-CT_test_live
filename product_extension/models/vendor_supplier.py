# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    is_primary = fields.Boolean(string='Is Primary',help='Default Vendor select')
    description = fields.Text(string='Description',help='Supplier Product Description',translate=True)
    stock = fields.Float(string='Stock',help="Total Stock Available with Supplier")
    preferred = fields.Integer(string='Preferred',help="Preferred")
    multiple = fields.Integer(string='Multiple')
    primary_vendor = fields.Boolean(Default=False)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template',index=True, ondelete='cascade', oldname='product_id')

    @api.onchange('product_id')
    def get_product_template(self):
    	if self.product_id:
    		self.product_tmpl_id = self.product_id.product_tmpl_id

    @api.model
    def create(self, vals):
        res = super(SupplierInfo, self).create(vals)
        if res.primary_vendor:
            vendor_ids=self.env["product.supplierinfo"].search([('primary_vendor','=',True),('id','!=',res.id),('product_id','=',res.product_id.id)])
            for rec in vendor_ids:
                rec.primary_vendor=False
        return res

    @api.multi
    def write(self,vals):
        res = super(SupplierInfo, self).write(vals)
        if self.primary_vendor:
            vendor_ids=self.env["product.supplierinfo"].search([('primary_vendor','=',True),('id','!=',self.id),('product_id','=',self.product_id.id)])
            for rec in vendor_ids:
                rec.primary_vendor=False
        return res
