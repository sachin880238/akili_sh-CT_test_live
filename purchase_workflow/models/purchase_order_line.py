from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'

    source_id = fields.Many2one('product.sources', string='Vendor Product')
    source_name = fields.Text(related='source_id.name', string='Vendor Product')
    vendor_product_id = fields.Many2one('vendor.product.product', related="source_id.vendor_product_id", string="Vendor Product")
    vendor_product_uom = fields.Many2one('uom.uom', related="source_id.uom_id", string='UOM')
    vendor_prod_minimum = fields.Integer(string='Minimum', related="source_id.minimum")
    vendor_prod_multiple = fields.Integer(string='Multiple', related="source_id.multiple")
    vendor_prod_qty = fields.Float(string="Quantity")
    vendor_route_id = fields.Many2one('stock.location.route', string="Route")
    vendor_carrier_id = fields.Many2one('delivery.carrier', string="Via")
    delivery_date = fields.Date(string="Date", default=fields.Date.today, readonly=True)
    vendor_price_id = fields.Many2one('vendor.price', related="source_id.vendor_price_id", string='Vendor Price')
    vendor_prod_lst_price = fields.Float(string='List', related="vendor_price_id.base_price")
    vendor_discount = fields.Float(string='Discount', related="vendor_price_id.discount")
    vendor_prod_unit_price = fields.Float(string='Unit Price', related="source_id.price")
    vendor_prod_net_price = fields.Monetary(string='Net Price', compute="_get_vendor_prod_net_price", store=True)

    @api.onchange('source_id')
    def default_minimum_vendor_prod_qty(self):
        if self.source_id:
            self.vendor_prod_qty = self.vendor_prod_minimum
            self.product_qty = self.product_minimum
        if not self.source_id:
            self.vendor_prod_qty = False
            self.vendor_prod_net_price = False
            self.product_qty = False

    @api.depends('vendor_prod_qty')
    def _get_vendor_prod_net_price(self):
        for record in self:
            record.vendor_prod_net_price = record.vendor_prod_qty * record.vendor_prod_unit_price

    product_id = fields.Many2one('product.product', related="source_id.product_id", string='Product', required=False, store=True)
    product_uom = fields.Many2one('uom.uom', string='UOM', related="source_id.product_unit", required=False, store=True)
    product_minimum = fields.Integer(string='Minimum', related="source_id.product_minimum", store=True)
    product_multiple = fields.Integer(string='Multiple', related="source_id.product_multiple", store=True)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=False, default=1)
    route_id = fields.Many2one('stock.location.route', string="Route")
    carrier_id = fields.Many2one('delivery.carrier', string="Via")
    lst_price = fields.Float(string='List', related="product_id.lst_price", store=True)
    discount = fields.Float(string='Discount', related="vendor_price_id.discount", store=True)
    price_unit = fields.Float(string='Unit Price', required=False,readonly=True)
    net_price = fields.Monetary(string='Net Price', compute="_get_net_price", store=True)

    @api.onchange('vendor_prod_qty', 'product_qty')
    def _get_prod_qty(self):
        if self.source_id:
            if self.vendor_tab:
                if self.source_id.qty < self.source_id.vendor_qty:
                    self.product_qty = (self.vendor_prod_qty * self.source_id.vendor_qty) / self.source_id.qty
                elif self.source_id.qty > self.source_id.vendor_qty:
                    self.product_qty = (self.vendor_prod_qty * self.source_id.qty) / self.source_id.vendor_qty
                else:
                    self.product_qty = self.vendor_prod_qty
            else:
                if self.source_id.qty < self.source_id.vendor_qty:
                    self.vendor_prod_qty = (self.product_qty * self.source_id.qty) / self.source_id.vendor_qty
                elif self.source_id.qty > self.source_id.vendor_qty:
                    self.vendor_prod_qty = (self.product_qty * self.source_id.vendor_qty) / self.source_id.qty
                else:
                    self.vendor_prod_qty = self.product_qty
            if self.vendor_tab:
                if self.vendor_prod_qty < self.vendor_prod_minimum:
                    raise ValidationError(_('Quantity can not be less than %s')%(self.vendor_prod_minimum))
                if self.vendor_prod_qty > self.vendor_prod_minimum:
                    if self.vendor_prod_qty % self.vendor_prod_multiple != 0:
                        raise ValidationError(_('Quantity field must be equal to multiple of %s')%(self.vendor_prod_multiple))
            # else:
            #     if self.product_multiple > 0 :
            #         if self.product_qty < self.product_minimum:
            #             raise ValidationError(_('Quantity can not be less than %s')%(self.product_minimum))
            #         if self.product_qty % self.product_multiple != 0:
            #             raise ValidationError(_('Quantity field must be equal to multiple of %s')%(self.product_multiple))

    @api.depends('product_qty')
    def _get_net_price(self):
        for record in self:
            record.net_price = record.product_qty * record.price_unit

    vendor_tab = fields.Boolean(string="Vendor Tab")
    is_bundle_item = fields.Boolean(string="Is Bundle Item", invisible=True)
    is_note = fields.Boolean(invisible=True)
    is_section = fields.Boolean(invisible=True)
    sequence = fields.Integer(string='Sequence')
    name = fields.Text(string='Product', required=False, compute="_get_product_name")

    def _get_product_name(self):
        for record in self:
            if record.product_id:
                if record.product_id.description_purchase:
                    record.name = record.product_id.full_name + '\n' + record.product_id.description_purchase
                else:
                    record.name = record.product_id.full_name

    order_id = fields.Many2one('purchase.order', string="Order ID")
    date_planned = fields.Datetime(string='Scheduled Date', default=fields.Datetime.now)
    desc = fields.Text(string="Note")
    vendor_stock = fields.Float(string="Stock")
    vendor_desc = fields.Text(string="Description")
    delivery = fields.Char(string="Delivery")
    cost_price = fields.Float(string="Cost")
    v_product_id = fields.Many2one('product.supplierinfo', string="Vendor Product")
    vendor_qty = fields.Integer(string="Vendor Quantity")

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        vendor_id = self.partner_id
        variant_seller_ids = self.product_id.variant_seller_ids
        if variant_seller_ids:
            for variant_seller in variant_seller_ids:
                if variant_seller.name == vendor_id and variant_seller.product_id == self.product_id:
                    self.vendor_stock = variant_seller.stock
                    self.vendor_desc = variant_seller.description
                    self.price_unit = variant_seller.price
                else:
                    self.price_unit = self.product_id.lst_price
                    self.vendor_stock = False
                    self.vendor_desc = False
        else:
            if self.discount:
                self.price_unit = self.lst_price - (self.lst_price * self.discount / 100)
        return res

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        vendor_id = self.partner_id
        variant_seller_ids = self.product_id.variant_seller_ids
        if variant_seller_ids:
            for variant_seller in variant_seller_ids:
                if variant_seller.name == vendor_id and variant_seller.product_id == self.product_id:
                    self.price_unit = variant_seller.price
                else:
                    self.price_unit = self.product_id.lst_price
        else:
            self.price_unit = self.lst_price - (self.lst_price * self.discount / 100)
            if self.product_qty:
                self.net_price = self.product_qty * self.price_unit
            else:
                self.net_price  = False
        return res

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.multi
    def add_po_line(self):
        return True

    @api.multi
    def add_new_po_line(self):
        if self.order_id and self.vendor_tab == False :
            return self.order_id.add_stockable_product()
        if self.order_id and self.vendor_tab == True :
            return self.order_id.add_vend_stockable_product()
