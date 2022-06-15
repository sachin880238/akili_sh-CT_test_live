# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_reserve_ship_invoiced_qty(self):
        #reserved_obj = self.env['reserved.products']
        move_obj = self.env['stock.move']
        stock_obj = self.env['stock.picking']
        #for line in self:
            #move_id = move_obj.search([('sale_line_id','=',line.id)])
            #reserve_id = reserved_obj.search([('product_id','=',line.product_id.id),('order_line','=',line.id)])
            #if reserve_id:
            #    line.reserver_qty = reserve_id.available + reserve_id.waiting
            #if move_id:
            #    if move_id.state == 'done':
            #        delivered_qty = 0
            #        for quant in move_id.quant_ids:
            #            delivered_qty += quant.qty
            #        line.shipped_qty = delivered_qty

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_so_line_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_so_line_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    is_bundel_item = fields.Boolean("Is Bundle Item")
    is_bundle = fields.Boolean("Is Bundle")
    bundle_id = fields.Many2one("product.product", 'Bundle ID')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict',)
    need_update = fields.Boolean("Need Update")   
    route_id = fields.Many2one('stock.location.route',string='Route')
    carrier_id = fields.Many2one('delivery.carrier',string='Via')

    warning = fields.Char(string='Warning')
    available = fields.Integer(string='Available')
    comment = fields.Text(string='Comment')
    product_template_id = fields.Many2one('product.template',string='Template', domain=[('sale_ok', '=', True), ('attribute_line_ids.value_ids', '!=', False)])

    # need to check
    available_days = fields.Float("Availability") 
    selected_line = fields.Boolean("S")
    delivery_date = fields.Datetime("Date", default=fields.Datetime.now)
    last_price = fields.Float(related='product_id.list_price', string="List")
    partner_id = fields.Many2one(related="order_id.partner_id", string="Account") 
    pricelist_id = fields.Many2one(related="order_id.pricelist_id", string="PriceList") 
    company_id = fields.Many2one(related="order_id.company_id", string="Company")
    #reserver_qty = fields.Float(compute=get_reserve_ship_invoiced_qty, string="Reserved", store=False)
    shipped_qty = fields.Float(compute=get_reserve_ship_invoiced_qty, string="Shipped", store=False)
    invoiced_qty = fields.Float(compute=get_reserve_ship_invoiced_qty, string="Invoiced", store=False) 
    ordered_qty = fields.Integer('Ordered')
    canceled_qty =fields.Integer('Canceled')
    required_qty = fields.Integer('Required')
    manufacture_qty = fields.Integer('Manufacture')
    transfer_quantity = fields.Integer('Transfer')
    shipment_quote = fields.Char('Shipment')
    bundle_quote = fields.Char('Bundle')
    is_reserved_stock = fields.Boolean('Is Reserved Stock', compute="get_is_reserve_stock")
    incoming_sale = fields.Integer('Incoming')
    shortage_sale = fields.Integer('Shortage', compute='get_shortage_qty')
    release_qty = fields.Integer('Released')
    reserved_qty = fields.Float(string="Reserved Qty",compute="_get_reserved_qty",store=False)
    differ_qty = fields.Float(string="Differ Qty")
    order_required = fields.Integer(string="Required Order")
    waiting_order = fields.Integer(string="Waiting Order")
    shipped_order = fields.Integer(string="Shipped")
    invoiced_order = fields.Integer(string="Invoiced Order")
    priority = fields.Selection([('x', 'Low'),('xx', 'Normal'), ('xxx', 'High'), ('xxxx', 'Urgent')],string='Priority')
    create_quot_date = fields.Datetime('Quotation Date', default=lambda self: fields.Datetime.now())
    is_sale_lines = fields.Boolean('Is Sale Lines', default=False)
    validity_date = fields.Date(string='Validity', readonly=True, related='order_id.validity_date')
    template_description = fields.Text('Description')
    cal_tax = fields.Monetary(string='Tax', store=True, readonly=True, compute='get_tax_compute_amount')

    @api.depends('tax_id')
    def get_tax_compute_amount(self):
        for line in self:
            if line.tax_id:
                line.cal_tax = line.tax_id.amount / 100
            

    @api.onchange('product_template_id', 'product_id')
    def _onchange_product_template_id(self):
        if self.product_template_id:
            self.template_description = self.product_template_id.description_quote
        if self.product_id:
            self.name_desc1 = self.product_id.description_quote
            self.warning = self.product_id.sale_line_warn_msg
            self.available = self.product_id.qty_available

    @api.multi
    def get_is_reserve_stock(self):
        for rec in self:
            if rec.order_id.stock_reserved:
                rec.is_reserved_stock = True
            else:
                rec.is_reserved_stock = False

    @api.depends('price_unit', 'discount')
    def get_discount_unit(self):
        for line in self:
          line.discount_unit = line.price_unit - ((line.discount * line.price_unit)/100)

    @api.depends('availability', 'incoming_sale')
    def get_shortage_qty(self):
        for line in self:
          line.shortage_sale = line.product_uom_qty - line.availability - line.incoming_sale

    discount_unit = fields.Float(compute=get_discount_unit, string="Unit", store='True')
    availability = fields.Integer(string='Available')  
    name_desc1 = fields.Text(string='Product')

    @api.multi
    @api.onchange('name_desc1')
    def product_name_desc1_change(self):
        if self.name_desc1 and self.product_id:
            name = self.product_id.name_get()[0][1]
            if name:
                self.name = name + '\n ' + self.name_desc1

    
    hold_qty = fields.Integer("Hold")
    expected_by = fields.Datetime(string="Validity Date")
    reserve_qty = fields.Float(string="Reserved")

    @api.multi
    @api.returns('self', lambda value: value.id)
    def carrier_id_change(self, carrier_id):
    	self.carrier_id = carrier_id
    	return self.order_id

    @api.multi
    def add_order_line(self):
        return True

    @api.multi
    def add_new_order_line(self):
        if self.order_id:
            return self.order_id.add_stockable_product()

    @api.multi
    def add_new_product_using_template(self):
        if self.order_id:
            return self.order_id.add_product_using_template()

    @api.model
    def create(self, vals):
        so_line = super(SaleOrderLine, self).create(vals)
        sale_line_obj = self.env['sale.order.line']
        for order_line in so_line.order_id.order_line:
            if order_line.is_bundle:
                bundle_id = order_line
                #bundle_id.price_unit += so_line.price_unit
                so_line.write({'bundle_id':so_line.product_id.id,
                          'is_bundel_item':True,
                          'price_tax': 0.0,
                          'price_total': 0.0,
                          'price_subtotal': 0.0,})
        return so_line
