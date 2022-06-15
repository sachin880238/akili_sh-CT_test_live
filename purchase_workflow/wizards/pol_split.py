from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class PolSplit(models.TransientModel):
    _name = "pol.split"
    _description = "Purchase order line Split"

    product_qty = fields.Float(string='Quantity')
    carrier_id = fields.Many2one('delivery.carrier',string='Via')
    route_id = fields.Many2one('stock.location.route',string='Mode')
    date_planned = fields.Datetime(string='Date')
    product_uom_qty_set = fields.Float(string='Quantity')
    carrier_id_set = fields.Many2one('delivery.carrier',string='Via')
    route_id_set = fields.Many2one('stock.location.route',string='Mode')
    delivery_date_set = fields.Datetime(string='Date')

    @api.model
    def default_get(self, fields_list):
        res = super(PolSplit, self).default_get(fields_list)
        purchase_order_line = self.env['purchase.order.line'].search([('id', 'in', self._context['select_order_line'])])     
        res['product_qty'] = purchase_order_line.product_uom_qty
        res['carrier_id'] =  purchase_order_line.carrier_id.id
        res['route_id'] = purchase_order_line.route_id.id
        res['date_planned'] = purchase_order_line.delivery_date
        res['carrier_id_set'] =  purchase_order_line.carrier_id.id
        res['route_id_set'] = purchase_order_line.route_id.id
        res['delivery_date_set'] = purchase_order_line.delivery_date
        return res 

    @api.multi
    def get_order_line_value(self,order_line):
        values = {
            'order_id': self._context.get('active_id'),
            'name': order_line.product_id.name,
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            # 'last_price': order_line.last_price,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit,
            'route_id': order_line.route_id.id,
            'carrier_id': order_line.carrier_id.id,
            'date_planned': order_line.date_planned,
            # 'reserve_qty': order_line.reserve_qty,
            'price_unit': order_line.product_id.lst_price,
            'uom_id' : order_line.product_id.uom_id.id
        }

        if self.carrier_id_set:
        	values['carrier_id'] = self.carrier_id_set.id
        if self.route_id_set:
        	values['route_id'] = self.route_id_set.id
        if self.delivery_date_set:
        	values['date_planned'] = self.delivery_date_set
        if self.product_uom_qty_set:
            values['product_qty'] = self.product_uom_qty_set	

        return values    


    @api.multi
    def split_line(self):
        po_line_obj = self.env['purchase.order.line']
        po_line_id = po_line_obj.search([('id', 'in', self._context['select_order_line'])])

        if not self.product_uom_qty_set > 0.0 or self.product_uom_qty_set >= po_line_id.product_qty:
        	raise UserError(_('Split quantity must not be larger, smaller or equal to quantity'))
        
        # if po_line_id.bundle_id:
        # 	raise UserError(_('You are not allowed to split the quantity of bundle item!!!'))
        
        if po_line_id:
            po_line_id.write({'product_qty': po_line_id.product_qty - self.product_uom_qty_set})
            
            for wizard in self:
                vals = wizard.get_order_line_value(po_line_id)
                vals['name']=po_line_id.product_id.full_name
                po_line = po_line_obj.with_context({'trigger_onchange': True,
                    'onchange_fields_to_trigger': ['product_id', 'product_qty']
                }).create(vals)
       	return True
