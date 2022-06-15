from odoo import models, fields, api


class VendorProductEquivalents(models.Model):

    _name = 'vendor.product.equivalents'
    _description = 'Vendor Product Equivalents'
    _rec_name = 'vendor_prod_id'

    sequence = fields.Integer(string='Sequence')
    name = fields.Text('Vendor Product', compute='get_equivalent_name')
    vendor_id = fields.Many2one('res.partner', string="Vendor", domain=[('supplier', '=', True),('parent_id', '=', False)])
    vendor_prod_qty = fields.Float('Quantity', default=1)
    vendor_prod_uom = fields.Many2one('uom.uom', string='Unit')
    vendor_prod_id = fields.Many2one('vendor.product.product', string='Vendor Product')
    vendor_prod_desc = fields.Text('Description')
    company_id = fields.Many2one('res.company', string='Company')
    product_qty = fields.Float(string='Quantity', default=1)
    product_id = fields.Many2one('product.product', string='Company Product')
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='Unit', store=True)
    uom_ids = fields.Many2many('uom.uom', related='vendor_prod_id.uom_ids')

    def get_equivalent_name(self):
        for equivalent in self:
            if equivalent.vendor_prod_id and equivalent.vendor_prod_desc:
                equivalent.name = equivalent.vendor_prod_id.complete_name + '\n' + equivalent.vendor_prod_desc
            else:
                equivalent.name = equivalent.vendor_prod_id.complete_name
