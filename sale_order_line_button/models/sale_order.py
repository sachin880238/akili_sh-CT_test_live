# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrder(models.Model):
    _inherit = "sale.order"

    update_price = fields.Boolean(
        string='Update price',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )


    def get_available_date(self, product_id, qty): 
        move_lines = self.env['stock.pack.operation'].search([('product_id','=',product_id.id),('qty_done','<',1)])  
        pr_dec = {} 
        for rec in move_lines: 
            pr_dec[rec.id] = {
                  'product_id':rec.product_id.id,
                  'qty':rec.product_qty,
                  'date':rec.picking_id.min_date, 
                             }
        if len(move_lines) > 1: 
            qty_temp = 0
            for val in sorted(pr_dec.values()): 
               qty_temp += val['qty']
               if qty_temp >= qty:
                   return val['date']
        elif move_lines:
            val = pr_dec.values()[0]
            if val['qty'] >= qty:
                   return val['date']
        return False



    # Add sale order line  
    @api.multi
    def add_stockable_product(self): 
        wizard_form = self.env.ref('sale_order_line_button.order_line_form_views')
        return {
            'name' : _('Add a Product'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'sale.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'order_line_type' : 'line', 'default_order_id': self.id}
        } 

    # Add Section line  
    @api.multi
    def add_section_product(self): 
        wizard_form = self.env.ref('sale_order_line_button.order_line_form_views')
        return {
            'name' : _('Add Section'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'sale.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'order_line_type' : 'line', 'default_order_id': self.id, 'default_display_type':'line_section'}
        }

    # Add sale order line template  
    @api.multi
    def add_product_using_template(self): 
        wizard_form = self.env.ref('sale_order_line_button.order_line_template_form_views')
        return {
            'name' : _('Add a Product from a Template'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'sale.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'order_line_type': 'line', 'default_order_id': self.id, 'open_product_configurator': True}
        }     

    # Add Note line  
    @api.multi
    def add_note_product(self): 
        wizard_form = self.env.ref('sale_order_line_button.order_line_form_views')
        return {
            'name' : _('Add Note'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'sale.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'order_line_type' : 'line', 'default_order_id': self.id, 'default_display_type':'line_note'}
        } 




    # Add Set Product
    @api.multi
    def add_set_product(self):
        wizard_form = self.env.ref('sale_order_line_button.sale_order_set_bundle_form_views') 
        return {
            'name' : _('Add a Product Set'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'sale.order.set.bundle',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'order_line_type': 'set','default_is_set':True}
        } 

    # Add Bundle Product
    @api.multi
    def add_bundle_product(self):
        sale_order_line = [] 
        wizard_form = self.env.ref('sale_order_line_button.sale_order_set_bundle_form_views')
        if self._context.get('o2m_selection'):
            sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
        return {
            'name' : _('Add a Product Bundle'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'sale.order.set.bundle',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'order_line_type' : 'bundle','default_is_bundle':True,'sale_order_line':sale_order_line}
        }     


    
    # Remove Bundle Product
    @api.multi
    def remove_bundle_product(self):
        line_obj = self.env['sale.order.line']
        order_lines = line_obj.search([('order_id','=',self.id),('is_bundel_item','=',True)])
        for line in order_lines:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.write({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'bundle_id':False,
                'is_bundel_item':False,
            })
        order_lines = line_obj.search([('order_id','=',self.id),('is_bundle','=',True)])
        order_lines.unlink()
        self.write({'update_price':False})


    # Check Stock base on location qty on hand   
    @api.multi
    def check_stock(self):
        if not self.env.context.get('o2m_selection'):
            raise UserError(_('Please select at least one order line to perform this action.'))

        sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
        sale_order_line_ids = self.env['sale.order.line'].browse(sale_order_line)
        for line in sale_order_line_ids:
            if line.product_id.id == False :
                 raise UserError(_('You have selected invalid order line that have invalid product.'))
            else:
                wizard_form = self.env.ref('sale_order_line_button.check_stock_views')
                vals = {
                    'name' : _('Check Stock'),
                    'type' : 'ir.actions.act_window',
                    'res_model' : 'check.stock',
                    'view_id' : wizard_form.id,
                    'view_type' : 'form',
                    'view_mode' : 'form',
                    'target': 'new',
                    'context': {}
                }
        if self.env.context.get('o2m_selection'):
            sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            sale_order_line_ids = self.env['sale.order.line'].browse(sale_order_line)
            order_lines = []
            completed_date_list = []
            for line in sale_order_line_ids:
                if not line.product_id:
                    continue
                avl_date = False 
                if line.product_uom_qty <= line.product_id.qty_available:
                    avl_date = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
                #else:
                #    avl_date = self.get_available_date(line.product_id,line.product_uom_qty)
                if avl_date:
                    completed_date_list.append(avl_date)
                #reserver_ids = self.env['reserved.products'].search([('product_id','=',line.product_id.id)])
                incoming_left = 0
                incoming_reserved = 0
                #for reserve in reserver_ids:
                #    incoming_reserved += reserve.waiting  
                incoming_left = line.product_id.incoming_qty -  incoming_reserved  
                val = {
                    'product_id':line.product_id.id,
                    'current_stock':line.product_id.qty_available,
                    'incoming_stock':incoming_left,
                    'requested_qty':line.product_uom_qty,
                    'expected_date' : avl_date
                }
                order_lines.append((0,0,val)) 
            vals['context'].update({
                'data_line' : order_lines,
                'default_data_line' : order_lines,
            })
            if completed_date_list:
                vals['context'].update({
                    'default_completed_date': max(completed_date_list),
                })
        return vals

    # set route for each product line    
    @api.multi
    def set_route(self):
        sale_order_line = [] 
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please Select at least One Order Line to Perform this Action!!!'))
        else:
            sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            sale_order_line_ids = self.env['sale.order.line'].browse(sale_order_line)
            for line in sale_order_line_ids:
                if line.product_id.id == False :
                     raise UserError(_('You have selected order line that have invalid product.'))

            wizard_form = self.env.ref('sale_order_line_button.set_route_views')
            return {
                'name' : _('Set Route'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'set.route',
                'view_id' : wizard_form.id,
                'view_type' : 'form',
                'view_mode' : 'form',
                'target': 'new',
                'context': {'sale_order_line':sale_order_line}
            }

    
    # set via for each product line     
    @api.multi
    def set_via(self):
        sale_order_line = [] 
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please select at least One Order Line to Perform this Action!!!'))
        else:
            sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            sale_order_line_ids = self.env['sale.order.line'].browse(sale_order_line)
            for line in sale_order_line_ids:
                if line.product_id.id == False :
                     raise UserError(_('You have selected order lines that have invalid product.'))

            wizard_form = self.env.ref('sale_order_line_button.set_via_views')
            return {
                'name' : _('Set Via'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'set.via',
                'view_id' : wizard_form.id,
                'view_type' : 'form',
                'view_mode' : 'form',
                'target': 'new',
                'context': {'sale_order_line':sale_order_line}
            }

    # set Date for each product line  
    @api.multi
    def set_date(self):
        sale_order_line = [] 
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please select at least One Order Line to Perform this Action!!!'))
        else:
            sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            sale_order_line_ids = self.env['sale.order.line'].browse(sale_order_line)
            for line in sale_order_line_ids:
                if line.product_id.id == False :
                     raise UserError(_('You have selected order lines that have invalid product.'))

            wizard_form = self.env.ref('sale_order_line_button.set_date_orderline_views')
            return {
                'name' : _('Set Date'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'set.date.orderline',
                'view_id' : wizard_form.id,
                'view_type' : 'form',
                'view_mode' : 'form',
                'target': 'new',
                'context': {'sale_order_line':sale_order_line}
            }

    # set Discount for each product line
    @api.multi
    def set_discount(self):
        sale_order_line = [] 
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please select at least One Order Line to Perform this Action!!!'))
        else:
            sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
            sale_order_line_ids = self.env['sale.order.line'].browse(sale_order_line)
            for line in sale_order_line_ids:
                if line.product_id.id == False :
                     raise UserError(_('You have selected order lines that have invalid product.'))

            wizard_form = self.env.ref('sale_order_line_button.set_discount_orderline_views')
            return {
                'name' : _('Set Discount'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'set.discount.orderline',
                'view_id' : wizard_form.id,
                'view_type' : 'form',
                'view_mode' : 'form',
                'target': 'new',
                'context': {'sale_order_line':sale_order_line}
            }

     # Sort line for each product line
    @api.multi
    def sort_lines(self):
        wizard_form = self.env.ref('sale_order_line_button.sort_orderline_views')
        return {
            'name' : _('Sort Lines'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'sort.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {}
        }
       
     # Merge lines for select product line 

    @api.multi
    def merge_lines(self):
        sale_order_lines = []
        list_id = [] 
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please Select at least Two Order Lines to Perform this Action!!!')) 

        wizard_form = self.env.ref('sale_order_line_button.merge_line_product_wizard_view')
        sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
        sale_order_line_ids = self.env['sale.order.line'].browse(sale_order_line)

        for rec in sale_order_line_ids:
            sale_order_lines.append(rec)
            if rec.product_id.id == False:
                    raise UserError(_('You have selected order line that have invalid product.'))
        
        if len(sale_order_lines) < 2:
            raise UserError(_('Please Select at least Two Order Lines to Perform this Action!!!'))

        for rec in sale_order_lines:
            if rec.product_id.id:
                list_id.append(rec.product_id.id)

        for temp in list_id:
            if not  list_id[0]== temp:
                raise UserError(_('Please select that order lines that have the same product.'))

        else:
            latest_date_list = []
            for line in sale_order_line_ids:
                if line.delivery_date:
                    # delivery_date = datetime.strftime(line.delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    latest_date_list.append(line.delivery_date)
                else:
                    latest_date_list = False

            return {
                'name' : _('Merge Lines'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'merge.order.line',
                'view_id' : wizard_form.id,
                'view_type' : 'form',
                'view_mode' : 'form',
                'target': 'new',
                'context': {
                    'default_latest_date': max(latest_date_list) if latest_date_list else '',
                    # 'active_order_line':
                    'default_line_ids': sale_order_line_ids.ids,
                    'selected_line_route_ids': sale_order_line_ids.mapped('route_id').ids,
                    'selected_line_carrier_ids': sale_order_line_ids.mapped('carrier_id').ids,
                }
            }    

    # Split line for select product line
    @api.multi
    def split_line(self):
        sale_order_line = [] 
        wizard_form = self.env.ref('sale_order_line_button.split_line_product_wizard_view')
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please Select anyone of the Order Lines to Perform this Action!!!'))
        else:
            sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')

        if len(sale_order_line) > 1:
            raise UserError(_('Please Select only One Order Line to Perform this Action!!!'))

        sale_order_line_ids = self.env['sale.order.line'].browse(sale_order_line)
        for rec in sale_order_line_ids:
            if rec.product_id.id == False:
                raise UserError(_('Please Select that Order Line that have vailid product.'))
            if rec.product_uom_qty <=1 :
                raise UserError(_('Please Select that Order Line that Quantity is more than one.'))

        
                
        return {
            'name' : _('Split Line'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'split.order.line',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'select_order_line': sale_order_line}
        }

    # Move line for select product line    
    @api.multi
    def move_line_option(self):
        sale_order_line = [] 
        wizard_form = self.env.ref('sale_order_line_button.move_lines_option_views')
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please Select at least One Line to Perform this Action!!!'))
        else:
            sale_order_line = self._context.get('o2m_selection').get('order_line').get('ids')
        
        return {
            'name' : _('Warning'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'move.lines.option',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'select_order_line': sale_order_line}
        }
