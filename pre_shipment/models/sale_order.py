# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"


    pre_shipment_lines = fields.One2many("pre.shipment", 'order_id', string='Pre Shipments')

    # need to check

    order_line = fields.One2many('sale.order.line', 'order_id', string='Quotation Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, widget="one2many_selectable" )

    @api.multi
    @api.onchange('order_line')
    def onchange_order_line_id(self):
        self.pre_shipment_lines = False

     # Merge lines for select product line    
    @api.multi
    def merge_shipment_lines(self):
        wizard_form = self.env.ref('quotation_shipment_line.merge_line_shipment_wizard_view')
        if not self._context.get('selected_o2m_ids') or (len(self._context.get('selected_o2m_ids'))==1):
            raise UserError(_('You Select at least two Line to Perform this Action!!!'))
        pre_shipments_ids = self.env['pre.shipment'].browse(self._context.get('selected_o2m_ids'))
        # if len(pre_shipments_ids.mapped('ship_lines').mapped('product_id')) != 1:
           #  raise UserError(_('You select ordelines which have same product!!!'))
        latest_date_list = []

        for line in pre_shipments_ids:
            if line.del_date:
               latest_date_list.append(line.del_date)
          
        return {
            'name' : _('Merge Lines'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'merge.order.line.shipment',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {
                'default_latest_date': max(latest_date_list) if latest_date_list else '',
                'default_line_ids': pre_shipments_ids.ids,
                'selected_line_route_ids': pre_shipments_ids.mapped('route_id').ids,
                'selected_line_carrier_ids': pre_shipments_ids.mapped('ship_via').ids,
            }
        }


    # this functiona from sale.py 440 line file in so_do_workflow module use in view file

    def generate_new_shipments(self):
        ship_obj = self.env['pre.shipment']
        ship_line_obj = self.env['pre.shipment.lines']
        not_carrier = any(not line.carrier_id for line in self.order_line)
        not_delivery_date = any(not line.delivery_date for line in self.order_line)
        not_route = any(not line.route_id for line in self.order_line)
        if not_route and not_carrier and not_delivery_date:    
            raise UserError(_('For Generate Pre Shipment Order lne not have Via,Mode and Delivery Date.'))
        if not_route and not_carrier:
            raise UserError(_('For Generate Pre Shipment Order lne not have Via and Mode.'))
        if not_route:
            raise UserError(_('For Generate Pre Shipment Order lne not have Mode.'))
        if not_carrier: 
            raise UserError(_('For Generate Pre Shipment Order lne not have Via.'))        
        if not_delivery_date:
            raise UserError(_('For Generate Pre Shipment Order lne not have Delivery Date.'))

        for line in self.order_line:
            vals = {
                'order_id':self.id,
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


    def get_total_shipment(self):
        return True

    def pay_shipment(self):
        return True

    def release_shipment(self):
        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pre_shipment_id = fields.Many2one("pre.shipment", string='Shipment')
    pre_ship_flag = fields.Boolean("Modify Ship")


    @api.multi
    def create_pre_shipment(self, vals):
        ship_obj = self.env['pre.shipment']
        ship_line_obj = self.env['pre.shipment.lines']
        ship_id = ship_obj.search([('order_id', '=', vals['order_id']),('del_date','=',vals['delivery_date']), 
                                   ('ship_via','=',vals['carrier_id']),('route_id','=',vals['route_id'])]) 
        if not ship_id: 
            ship_id = ship_obj.create({'order_id':vals['order_id'], 'ship_via':vals['carrier_id'],
                                       'del_date':vals['delivery_date'], 'route_id':vals['route_id']}) 
            ship_line_id = ship_line_obj.create({'pre_ship_id':ship_id.id, 'product_id':vals['product_id'], 
                                                 'name':vals['name'], 'product_uom_qty':vals['product_uom_qty'],
                                                 'price_unit':vals['price_unit']}) 
        else: 
            ship_line_id = ship_line_obj.search([('pre_ship_id', '=', ship_id.id),('product_id','=',vals['product_id'])])
            if not ship_line_id: 
                ship_line_id = ship_line_obj.create({'pre_ship_id':ship_id.id, 'product_id':vals['product_id'], 
                                                 'name':vals['name'], 'product_uom_qty':vals['product_uom_qty'],
                                                 'price_unit':vals['price_unit']}) 
            else: 
                ship_line_id.write({'product_uom_qty':ship_line_id.product_uom_qty + vals['product_uom_qty'],
                                    'price_unit':ship_line_id.price_unit + vals['price_unit']})
        return ship_id.id

    def update_pre_shipment(self, vals):
        ship_obj = self.env['pre.shipment']
        ship_line_obj = self.env['pre.shipment.lines']
        ship_id = ship_obj.search([('order_id', '=', self.order_id.id), ('del_date', '=', self.delivery_date),
                                   ('ship_via', '=', self.carrier_id.id), ('route_id', '=', self.route_id.id)])
        if ship_id:
            line_val = {}
            ship_line_id = ship_line_obj.search(
                [('pre_ship_id', '=', ship_id.id), ('product_id', '=', self.product_id.id)])
            if 'carrier_id' in vals:
                if ship_line_id.product_uom_qty != self.product_uom_qty:
                    ship_line_id.write({'product_uom_qty': ship_line_id.product_uom_qty - self.product_uom_qty,
                                        'price_unit': ship_line_id.price_unit - self.price_unit})
                else:
                    ship_line_id.unlink()
                    if len(ship_id.ship_lines) == 0:
                        ship_id.unlink()
                ship_id = False
                if 'delivery_date' in vals and 'route_id' not in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', vals['delivery_date']),
                         ('ship_via', '=', vals['carrier_id']), ('route_id', '=', self.route_id.id)])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': vals['carrier_id'],
                                                   'del_date': vals['delivery_date'], 'route_id': self.route_id.id})
                elif 'delivery_date' not in vals and 'route_id' not in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', self.delivery_date),
                         ('ship_via', '=', vals['carrier_id']), ('route_id', '=', self.route_id.id)])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': vals['carrier_id'],
                                                   'del_date': self.delivery_date, 'route_id': self.route_id.id})
                elif 'route_id' in vals and 'delivery_date' in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', vals['delivery_date']),
                         ('ship_via', '=', vals['carrier_id']), ('route_id', '=', vals['route_id'])])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': vals['carrier_id'],
                                                   'del_date': vals['delivery_date'], 'route_id': vals['route_id']})
                elif 'delivery_date' not in vals and 'route_id' in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', self.delivery_date),
                         ('ship_via', '=', vals['carrier_id']), ('route_id', '=', vals['route_id'])])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': vals['carrier_id'],
                                                   'del_date': self.delivery_date, 'route_id': vals['route_id']})
                if 'product_uom_qty' in vals:
                    line_val['product_uom_qty'] = vals['product_uom_qty']
                else:
                    line_val['product_uom_qty'] = self.product_uom_qty
                if 'price_unit' in vals:
                    line_val['price_unit'] = vals['price_unit']
                else:
                    line_val['price_unit'] = self.price_unit
                ship_line_id = ship_line_obj.search(
                    [('pre_ship_id', '=', ship_id.id), ('product_id', '=', self.product_id.id)])
                if not ship_line_id:
                    line_val['pre_ship_id'] = ship_id.id
                    line_val['product_id'] = self.product_id.id
                    line_val['name'] = self.name
                    ship_line_id = ship_line_obj.create(line_val)

                else:
                    ship_line_id.write({'product_uom_qty': ship_line_id.product_uom_qty + line_val['product_uom_qty'],
                                        'price_unit': ship_line_id.price_unit + line_val['price_unit']})
                return ship_id.id
            if 'delivery_date' in vals:
                if ship_line_id.product_uom_qty != self.product_uom_qty:
                    ship_line_id.write({'product_uom_qty': ship_line_id.product_uom_qty - self.product_uom_qty,
                                        'price_unit': ship_line_id.price_unit - self.price_unit})
                else:
                    ship_line_id.unlink()
                    if len(ship_id.ship_lines) == 0:
                        ship_id.unlink()
                ship_id = False
                if 'carrier_id' in vals and 'route_id' not in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', vals['delivery_date']),
                         ('ship_via', '=', vals['carrier_id']), ('route_id', '=', self.route_id.id)])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': vals['carrier_id'],
                                                   'del_date': vals['delivery_date'], 'route_id': self.route_id.id})
                elif 'carrier_id' not in vals and 'route_id' not in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', vals['delivery_date']),
                         ('ship_via', '=', self.carrier_id.id), ('route_id', '=', self.route_id.id)])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': self.carrier_id.id,
                                                   'del_date': vals['delivery_date'], 'route_id': self.route_id.id})
                elif 'route_id' in vals and 'carrier_id' in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', vals['delivery_date']),
                         ('ship_via', '=', vals['carrier_id']), ('route_id', '=', vals['route_id'])])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': vals['carrier_id'],
                                                   'del_date': vals['delivery_date'], 'route_id': vals['route_id']})
                elif 'carrier_id' not in vals and 'route_id' in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', vals['delivery_date']),
                         ('ship_via', '=', self.carrier_id.id), ('route_id', '=', vals['route_id'])])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': self.carrier_id.id,
                                                   'del_date': vals['delivery_date'], 'route_id': vals['route_id']})
                if 'product_uom_qty' in vals:
                    line_val['product_uom_qty'] = vals['product_uom_qty']
                else:
                    line_val['product_uom_qty'] = self.product_uom_qty
                if 'price_unit' in vals:
                    line_val['price_unit'] = vals['price_unit']
                else:
                    line_val['price_unit'] = self.price_unit
                ship_line_id = ship_line_obj.search(
                    [('pre_ship_id', '=', ship_id.id), ('product_id', '=', self.product_id.id)])
                if not ship_line_id:
                    line_val['pre_ship_id'] = ship_id.id
                    line_val['product_id'] = self.product_id.id
                    line_val['name'] = self.name
                    ship_line_id = ship_line_obj.create(line_val)

                else:
                    ship_line_id.write({'product_uom_qty': ship_line_id.product_uom_qty + line_val['product_uom_qty'],
                                        'price_unit': ship_line_id.price_unit + line_val['price_unit']})
                return ship_id.id
            if 'route_id' in vals:
                if ship_line_id.product_uom_qty != self.product_uom_qty:
                    ship_line_id.write({'product_uom_qty': ship_line_id.product_uom_qty - self.product_uom_qty,
                                        'price_unit': ship_line_id.price_unit - self.price_unit})
                else:
                    ship_line_id.unlink()
                    if len(ship_id.ship_lines) == 0:
                        ship_id.unlink()
                ship_id = False
                if 'carrier_id' in vals and 'delivery_date' not in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', self.delivery_date),
                         ('ship_via', '=', vals['carrier_id']), ('route_id', '=', vals['route_id'])])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': vals['carrier_id'],
                                                   'del_date': self.delivery_date, 'route_id': vals['route_id']})
                elif 'carrier_id' not in vals and 'delivery_date' not in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', self.delivery_date),
                         ('ship_via', '=', self.carrier_id.id), ('route_id', '=', vals['route_id'])])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': self.carrier_id.id,
                                                   'del_date': self.delivery_date, 'route_id': vals['route_id']})
                elif 'delivery_date' in vals and 'carrier_id' in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', vals['delivery_date']),
                         ('ship_via', '=', vals['carrier_id']), ('route_id', '=', vals['route_id'])])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': vals['carrier_id'],
                                                   'del_date': vals['delivery_date'], 'route_id': vals['route_id']})
                elif 'carrier_id' not in vals and 'delivery_date' in vals:
                    ship_id = ship_obj.search(
                        [('order_id', '=', self.order_id.id), ('del_date', '=', vals['delivery_date']),
                         ('ship_via', '=', self.carrier_id.id), ('route_id', '=', vals['route_id'])])
                    if not ship_id:
                        ship_id = ship_obj.create({'order_id': self.order_id.id, 'ship_via': self.carrier_id.id,
                                                   'del_date': vals['delivery_date'], 'route_id': vals['route_id']})
                if 'product_uom_qty' in vals:
                    line_val['product_uom_qty'] = vals['product_uom_qty']
                else:
                    line_val['product_uom_qty'] = self.product_uom_qty
                if 'price_unit' in vals:
                    line_val['price_unit'] = vals['price_unit']
                else:
                    line_val['price_unit'] = self.price_unit
                ship_line_id = ship_line_obj.search(
                    [('pre_ship_id', '=', ship_id.id), ('product_id', '=', self.product_id.id)])
                if not ship_line_id:
                    line_val['pre_ship_id'] = ship_id.id
                    line_val['product_id'] = self.product_id.id
                    line_val['name'] = self.name
                    ship_line_id = ship_line_obj.create(line_val)

                else:
                    ship_line_id.write({'product_uom_qty': ship_line_id.product_uom_qty + line_val['product_uom_qty'],
                                        'price_unit': ship_line_id.price_unit + line_val['price_unit']})
                return ship_id.id

    def unlink_pre_shipment(self):
        ship_line_obj = self.env['pre.shipment.lines']
        if self.pre_shipment_id:
            ship_line_id = ship_line_obj.search([('pre_ship_id', '=', self.pre_shipment_id.id),
                                                 ('product_id', '=', self.product_id.id)])
            if ship_line_id:
                if ship_line_id.product_uom_qty != self.product_uom_qty:
                    ship_line_id.write({'product_uom_qty': ship_line_id.product_uom_qty - self.product_uom_qty,
                                        'price_unit': ship_line_id.price_unit - self.price_unit})
                else:
                    ship_line_id.unlink()
                    if len(self.pre_shipment_id.ship_lines) == 0:
                        self.pre_shipment_id.unlink()
            return True
