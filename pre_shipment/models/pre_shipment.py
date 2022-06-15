# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api,_
from odoo.exceptions import UserError
import logging

class PreShipment(models.Model):
    _name = 'pre.shipment'
    _description = 'Pre Shipment'


    order_id = fields.Many2one("sale.order", string='Sale Order')
    name = fields.Char('Product', readonly=True)
    shipping_quantity = fields.Integer('Quantity')
    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)]) 
    ship_via = fields.Many2one("delivery.carrier", string='Via')
    del_date = fields.Date(string="Date")
    pro_cost = fields.Float(string="Products", compute='get_total_cost',  store=True)
    ship_cost = fields.Float( string="Shipping")
    service_cost = fields.Float(string="Services")
    tax_id = fields.Float(string="Tax")
    total = fields.Float(string="Value")
    priority = fields.Selection([('x', 'Low'),('xx', 'Normal'), ('xxx', 'High'), ('xxxx', 'Urgent')],string='Priority')
    state = fields.Selection([('draft', 'Draft'),('estimated', 'Estimated'),],  
                               string='State', default='draft')
    ship_lines = fields.One2many('pre.shipment.lines', 'pre_ship_id', string='Pre Shippment Lines',)
    required = fields.Integer(string="required")
    shipment_discount_unit = fields.Float(string="Unit", readonly=True)
    shipment_price_unit = fields.Float(string="List", readonly=True)
    shipment_discount = fields.Float(string="Disc", readonly=True)
    shipment_price_subtotal = fields.Float(string="Net", readonly=True)
    


    @api.depends('ship_lines.total_price')
    def get_total_cost(self):
        for rec in self:
            total_price = 0
            for line in rec.ship_lines:
                total_price += line.total_price
            rec.pro_cost = total_price

    @api.multi
    def generate_shippments(self,ids):
        ship_obj = self.env['pre.shipment']
        ship_line_obj = self.env['pre.shipment.lines'] 
        sale_order_rec = self.env['sale.order.line'].search([('id','=',ids[0][0][1])]).order_id
        for line in sale_order_rec.order_line:
            vals = {
                'order_id':sale_order_rec.id,
                'carrier_id':line.carrier_id.id,
                'delivery_date':line.delivery_date,
                'route_id':line.route_id.id,
                'product_id':line.product_id.id,
                'name':line.name,
                'product_uom_qty':line.product_uom_qty,
                'price_unit':line.price_unit,
            }
            ship_id = line.create_pre_shipment(vals)
            line.write({'pre_shipment_id':ship_id})
        return True

    @api.multi
    def update_order_lines(self, vals):
        order_lne_obj = self.env['sale.order.line']
        for rec in self:
            if 'route_id' in vals or 'ship_via' in vals or 'del_date' in vals:
                order_line_ids = order_lne_obj.search([('order_id','=',rec.order_id.id),('delivery_date','=',rec.del_date), 
                                   ('carrier_id','=',rec.ship_via.id),('route_id','=',rec.route_id.id)])
                if 'ship_via' in vals and 'route_id' in vals and 'del_date' in vals:
                    order_line_ids.write({'carrier_id':vals['ship_via'],'route_id':vals['route_id'],
                                          'delivery_date':vals['del_date'],'pre_ship_flag':True})
                if 'ship_via' not in vals and 'route_id' in vals and 'del_date' in vals:
                    order_line_ids.write({'route_id':vals['route_id'],'delivery_date':vals['del_date'],'pre_ship_flag':True})
                if 'ship_via' in vals and 'route_id' not in vals and 'del_date' in vals:
                    order_line_ids.write({'carrier_id':vals['ship_via'],'delivery_date':vals['del_date'],'pre_ship_flag':True})
                if 'ship_via' in vals and 'route_id' in vals and 'del_date' not in vals:
                    order_line_ids.write({'carrier_id':vals['ship_via'],'route_id':vals['route_id'],
                                          'delivery_date':vals['del_date'],'pre_ship_flag':True})
                if 'ship_via' not in vals and 'route_id' not in vals and 'del_date' in vals:
                    order_line_ids.write({'delivery_date':vals['del_date'],'pre_ship_flag':True})
                if 'ship_via' not in vals and 'route_id' in vals and 'del_date' not in vals:
                    order_line_ids.write({'route_id':vals['route_id'],'pre_ship_flag':True})
                if 'ship_via' in vals and 'route_id' not in vals and 'del_date' not in vals:
                    order_line_ids.write({'carrier_id':vals['ship_via'],'pre_ship_flag':True})
        return True

    @api.multi
    def get_new_ship_name(self, order_id):
        sale_rec = self.env['sale.order'].search([('id','=',order_id)])
        ship_ids = self.search([('order_id','=',order_id)])
        return sale_rec.name + '-' + str(len(ship_ids)+1)

    @api.model
    def create(self, vals):
        vals['name'] = self.get_new_ship_name(vals['order_id'])  
        res = super(PreShipment, self).create(vals) 
        return res


    @api.multi
    def write(self, vals):
        self.update_order_lines(vals)
        res = super(PreShipment, self).write(vals)
        return res
                 

class PreShipmentLines(models.Model):
    _name = 'pre.shipment.lines'
    _description = 'Pre Shipment Lines'


    pre_ship_id = fields.Many2one('pre.shipment', string='Pre Shippment') 
    product_id = fields.Many2one('product.product', string='Product') 
    name = fields.Char("Description")
    product_uom_qty = fields.Float("Quantity")
    price_unit = fields.Float("Unit Price")
    total_price = fields.Float("Total Price", compute='get_total_cost',  store=True)



    @api.depends('price_unit', 'product_uom_qty')
    def get_total_cost(self):
        for rec in self:
            rec.total_price = rec.price_unit * rec.product_uom_qty 
