from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class SplitOrderLine(models.TransientModel):
    _name = "split.order.line"
    _description = "Split Order Line"

    product_uom_qty = fields.Float(string='Quantity')
    carrier_id = fields.Many2one('delivery.carrier',string='Via')
    route_id = fields.Many2one('stock.location.route',string='Mode')
    delivery_date = fields.Datetime(string='Date')
    product_uom_qty_set = fields.Float(string='Quantity')
    carrier_id_set = fields.Many2one('delivery.carrier',string='Via')
    route_id_set = fields.Many2one('stock.location.route',string='Mode')
    delivery_date_set = fields.Datetime(string='Date')

    @api.model
    def default_get(self, fields_list):
        res = super(SplitOrderLine, self).default_get(fields_list)
        sale_order_line = self.env['sale.order.line'].search([('id', 'in', self._context['select_order_line'])])     
        res['product_uom_qty'] = sale_order_line.product_uom_qty
        res['carrier_id'] =  sale_order_line.carrier_id.id
        res['route_id'] = sale_order_line.route_id.id
        res['delivery_date'] = sale_order_line.delivery_date
        res['carrier_id_set'] =  sale_order_line.carrier_id.id
        res['route_id_set'] = sale_order_line.route_id.id
        res['delivery_date_set'] = sale_order_line.delivery_date
        return res 

    @api.multi
    def get_order_line_value(self,order_line):
        values = {
            'order_id': self._context.get('active_id'),
            'name': order_line.product_id.name,
            'product_id': order_line.product_id.id,
            'name_desc1': order_line.name_desc1,
            'product_uom_qty': order_line.product_uom_qty,
            'last_price': order_line.last_price,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit,
            'route_id': order_line.route_id.id,
            'carrier_id': order_line.carrier_id.id,
            # 'move_generated': order_line.move_generated,
            'delivery_date': order_line.delivery_date,
            'pre_shipment_id': order_line.pre_shipment_id.id,
            'reserve_qty': order_line.reserve_qty,
            'product_uom_qty': self.product_uom_qty_set,
            'price_unit': order_line.product_id.lst_price,
            'uom_id' : order_line.product_id.uom_id.id
        }

        if self.carrier_id_set:
        	values['carrier_id'] = self.carrier_id_set.id
        if self.route_id_set:
        	values['route_id'] = self.route_id_set.id
        if self.delivery_date_set:
        	values['delivery_date'] = self.delivery_date_set	

        return values    


    @api.multi
    def split_line(self):
        sale_line_obj = self.env['sale.order.line']
        sale_line_id = sale_line_obj.search([('id', 'in', self._context['select_order_line'])])
        if not self.product_uom_qty > 0.0:
        	raise UserError(_('You are not allowed to split selected orderline because quantity is Zero!!!'))
        if not self.product_uom_qty_set > 0.0 or self.product_uom_qty_set >= sale_line_id.product_uom_qty:
        	raise UserError(_('Ivalid quantity'))
        if sale_line_id.bundle_id:
        	raise UserError(_('You are not allowed to split the quantity of bundle item!!!'))
        if sale_line_id:
            sale_line_id.write({'product_uom_qty': sale_line_id.product_uom_qty - self.product_uom_qty_set})
            for wizard in self:
                vals = wizard.get_order_line_value(sale_line_id)
                vals['name']=sale_line_id.product_id.full_name
                so_line = sale_line_obj.with_context({'trigger_onchange': True,
                    'onchange_fields_to_trigger': ['product_id', 'product_uom_qty']
                }).create(vals)
       	return True
