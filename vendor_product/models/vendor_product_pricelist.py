from odoo import models, fields, api
from datetime import date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round

class VendorPrice(models.Model):

    _name = 'vendor.price'
    _description = 'Vendor Product Pricelist'

    def _get_end_date(self):
        current_date = fields.Date.context_today(self)
        end_date = current_date.replace(month=12)
        end_date_day = end_date.replace(day=31)
        return end_date_day

    name = fields.Char(compute='_compute_vendor_price_name')
    sequence = fields.Integer(string='Sequence')
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier', '=', True)], required=True)
    active = fields.Boolean(string='Active',
                            help="If unchecked, it will allow you to hide the pricelist without removing it.")
    product_tmpl_id = fields.Many2one('vendor.product.template', 'Template')
    product_id = fields.Many2one('vendor.product.product', 'Vendor Product')
    price = fields.Float(string='Net Price', compute='_compute_net_price', store=True)
    price_txt = fields.Char(string='Net Price', compute='_compute_price_txt', store=True)
    currency = fields.Many2one('res.currency', related='vendor_id.pur_currency_id', string='Currency')
    minimum = fields.Float(string='Minimum', required=True, default=1)
    minimum_txt = fields.Char(string='Minimum', compute='_compute_min_max_txt', store=True)
    multiple = fields.Float(string='Multiple', required=True, default=1)
    multiple_txt = fields.Char(string='Multiple', compute='_compute_min_max_txt', store=True)
    start_date = fields.Date(string='Starting', default=fields.Date.context_today)
    end_date = fields.Date(string='Ending', default=_get_end_date)
    days = fields.Integer(string='Days')
    state = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], default='draft')
    uom_ids = fields.Many2many('uom.uom', related='product_id.uom_ids')
    tmpl_uom_ids = fields.Many2many('uom.uom', related='product_tmpl_id.uom_ids')
    uom_id = fields.Many2one('uom.uom', string='Unit')
    base_price = fields.Float(string='Base Price')
    desc = fields.Text(string='Comments')
    discount = fields.Float(string='Discount')
    preferred = fields.Boolean(string='Preferred')
    temp_preferred = fields.Boolean(string='TPreferred')
    template_price_id = fields.Many2one('vendor.price')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_vendor_prices_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_vendor_prices_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    @api.onchange('preferred')
    def _onchange_preferred(self):
        if self.preferred:
            self.temp_preferred = True    

    @api.multi
    @api.onchange('base_price', 'uom_id')
    def _onchange_price(self):
        if all([self.base_price, self.uom_id]):
            self.state = 'active'
        else:
            self.state = 'draft'

    @api.depends('discount', 'base_price')
    def _compute_net_price(self):
        for record in self:
            if record.discount and record.base_price:
                discount = record.base_price * (record.discount / 100)
                record.price = record.base_price - discount
            elif record.base_price:
                record.price = record.base_price

    @api.depends('price', 'currency', 'uom_id')
    def _compute_price_txt(self):
        for record in self:
            if record.currency and record.uom_id:
                record.price_txt = str(record.currency.symbol) + str(round(record.price, 2)) + '/' + str(record.uom_id.name)
            elif record.currency:
                record.price_txt = str(record.currency.symbol) + str(round(record.price, 2))
            elif record.uom_id:
                record.price_txt = str(round(record.price, 2)) + '/' + str(record.uom_id.name)
            else:
                record.price_txt = str(round(record.price, 2))

    @api.depends('uom_id', 'multiple', 'minimum')
    def _compute_min_max_txt(self):
        for record in self:
            if record.uom_id:
                record.minimum_txt = str(record.minimum) + ' ' + str(record.uom_id.name)
                record.multiple_txt = str(record.multiple) + ' ' + str(record.uom_id.name)
            else:
                record.minimum_txt = str(record.minimum)
                record.multiple_txt = str(record.multiple)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        if self.product_tmpl_id.product_variant_count <= 1:
            self.product_id = self.product_tmpl_id.product_variant_ids

    @api.depends('vendor_id', 'product_id')
    def _compute_vendor_price_name(self):
        for rec in self:
            if rec.vendor_id and rec.product_id:
                rec.name = rec.vendor_id.name + ', ' + rec.product_id.name
            elif rec.vendor_id:
                rec.name = rec.vendor_id.name
            else:
                rec.name = rec.product_id.name

    def active_vendor_price(self):
        self.write({'state': 'active'})
        
    def deactivate_vendor_price(self):
        self.write({'state': 'inactive'})

    def reset_to_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        price = super(VendorPrice, self).create(vals)
        if 'temp_status' not in vals:
            if 'product_tmpl_id' in vals:
                if vals['product_id'] == False :
                    product_template_id = self.env['vendor.product.template'].search([('id','=',vals['product_tmpl_id'])])
                    for variant_id in product_template_id.product_variant_ids:
                        price_vals = {    
                            'base_price': price.base_price,
                            'currency': price.currency.id,
                            'uom_id': price.uom_id.id,
                            'discount': price.discount,
                            'price_txt': price.price_txt,
                            'minimum': price.minimum,
                            'multiple': price.multiple,
                            'start_date': price.start_date,
                            'end_date': price.end_date,
                            'preferred': price.preferred,
                            'desc': price.desc,
                            'vendor_id' : product_template_id.vendor_id.id,
                            'state':price.state,
                            'template_price_id':price.id
                            }
                        vp_price = variant_id.write({'vendor_price_ids':[(0,0,price_vals)]})
        return price

    @api.multi
    def write(self, vals):
        if vals.get('preferred'):
            preferred_vendor_price = self.search([('vendor_id', '=', self.vendor_id.id),
                                            ('product_id', '=', self.product_id.id),
                                            ('preferred', '=', True),
                                            ('id', '!=', self.id)])
            if preferred_vendor_price:
                preferred_vendor_price.write({'preferred': False})
        for rec in self:
            if not rec.template_price_id:
                price_ids = self.env['vendor.price'].search([('template_price_id','=',rec.id)])
                for price in price_ids:
                    price.write(vals)

        result = super(VendorPrice, self).write(vals)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            if not rec.template_price_id:
                price_ids = self.env['vendor.price'].search([('template_price_id','=',rec.id)])
                for price in price_ids:
                    price.unlink()
        res = super(VendorPrice, self).unlink()
        return res
