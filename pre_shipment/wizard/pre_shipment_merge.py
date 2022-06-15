# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PreShipmentMerge(models.TransientModel):
    _name = "pre.shipment.merge"
    _description = 'Pre Shipment merge'

    latest_date = fields.Date(string='Date')
    carrier_id = fields.Many2one('delivery.carrier',string='Via')
    route_id = fields.Many2one('stock.location.route',string='Route')


    @api.multi
    def merge_shipments(self):
        if self.env.context.get('selected_o2m_ids'):
            pre_shipments_ids = self.env['pre.shipment'].browse(self._context.get('selected_o2m_ids'))
            sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))

            tax_id = 0.0
            service_cost = 0.0
            ship_cost = 0.0
            total = 0.0
            for pre_ship in pre_shipments_ids:
                tax_id += pre_ship.tax_id
                service_cost += pre_ship.service_cost
                ship_cost += pre_ship.ship_cost
                total += pre_ship.total

            selected_pre_shipment = pre_shipments_ids.search([
                ('route_id','=',self.route_id.id),
                ('ship_via','=',self.carrier_id.id)])
    
            ship_lines =  pre_shipments_ids.mapped('ship_lines')
            if selected_pre_shipment:
                selected_pre_shipment.write({
                        'tax_id': tax_id,
                        'total': total,
                        'service_cost': service_cost,
                        'ship_cost': ship_cost,
                        'del_date': self.latest_date
                    })
                for line in ship_lines:
                    product_merge = False
                    if line in selected_pre_shipment.ship_lines:
                        continue
                    for selected_line in selected_pre_shipment.ship_lines:
                        if line.product_id == selected_line.product_id:
                            quantity = line.product_uom_qty + selected_line.product_uom_qty
                            selected_line.write({'product_uom_qty': quantity})
                            product_merge = True    
                    if not product_merge:    
                        line.write({'pre_ship_id':selected_pre_shipment.id})

                pre_shipments_ids = pre_shipments_ids - selected_pre_shipment
                pre_shipments_ids.unlink()        
            else:
                new_pre_shipment = self.env['pre.shipment'].create({
                    'order_id': sale_order.id,
                    'route_id': self.route_id.id,
                    'ship_via': self.carrier_id.id,
                    'del_date': self.latest_date,
                    'tax_id': tax_id,
                    'total': total,
                    'service_cost': service_cost,
                    'ship_cost': ship_cost,
                })
                
                for line in ship_lines:
                    product_merge = False
                    for new_line in new_pre_shipment.ship_lines:
                        if line.product_id == new_line.product_id:
                            quantity = line.product_uom_qty + new_line.product_uom_qty
                            new_line.write({'product_uom_qty': quantity})
                            product_merge = True    
                    if not product_merge:    
                        line.write({'pre_ship_id':selected_pre_shipment.id})
                    line.write({'pre_ship_id':new_pre_shipment.id})

                pre_shipments_ids.unlink()    
            return True