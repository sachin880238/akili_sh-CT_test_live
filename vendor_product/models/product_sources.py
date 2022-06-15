from odoo import api, fields, models


class ProductSources(models.Model):
    _name = 'product.sources'
    _description = 'Product Sources'

    sequence = fields.Integer(string='Sequence')
    default = fields.Boolean(string='Default')
    temp_default = fields.Boolean(string='TTDefault')
    name = fields.Text(related='equivalents_id.name', string='Vendor Product')
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier', '=', 'True')])
    vendor_product_id = fields.Many2one('vendor.product.product', string='Vendor Product')
    vendor_price_id = fields.Many2one('vendor.price', string='Vendor Price')
    price_state = fields.Selection(related="vendor_price_id.state", store=True)
    equivalents_id = fields.Many2one('vendor.product.equivalents', string='Equivalents')
    price = fields.Float(string='Price')
    delivered = fields.Float(string='Delivered')
    currency_id = fields.Many2one('res.currency', string='Currency')
    uom_id = fields.Many2one('uom.uom', string='Unit')
    minimum = fields.Integer(string='Minimum')
    multiple = fields.Integer(string='Multiple')
    effective = fields.Date(string='Effective')
    expiration = fields.Date(string='Expiration')
    days = fields.Integer(string='Days')
    vendor_desc = fields.Char(string='Description')
    vendor_qty = fields.Float(string='Quantity')

    # Product Fields
    company_id = fields.Many2one('res.company', string='Company')
    product_id = fields.Many2one('product.product', string='Product')
    product_tmpl_id = fields.Many2one('product.template', string='Template')
    desc = fields.Char(string='Description')
    qty = fields.Integer(string='Quantity')
    product_unit = fields.Many2one('uom.uom', string='Unit')
    lst_price = fields.Float(string='Price')
    product_currency = fields.Many2one('res.currency', string='Currency')
    product_minimum = fields.Integer(string='Minimum')
    product_multiple = fields.Integer(string='Multiple')
    product_effective = fields.Date(string='Effective')
    product_expiration = fields.Date(string='Expiration')
    ship_days = fields.Integer(string='Days')



    @api.onchange('default')
    def _onchange_default(self):
        if self.default:
            self.temp_default = True    

    
