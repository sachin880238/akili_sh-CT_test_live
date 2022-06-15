from odoo import models, api, fields, _
from odoo.exceptions import UserError


class PolSetBunble(models.TransientModel):
    _name = "pol.set.bundle"
    _description = "Purchase order line Set Bundle"

    quantity_to_add  = fields.Float(string='Quantity to Add',default=1)
    quantity_available = fields.Integer(string='Availability')
    is_set = fields.Boolean(
        string='Is Set',
        required=False,
        readonly=False,
        index=False,
        default=False,
    )

    is_bundle = fields.Boolean(
        string='Is bundle',
        required=False,
        readonly=False,
        index=False,
        default=False,
    )
    product_id = fields.Many2one('product.product',  string='Product', required=True)

    @api.multi
    def add_product_in_order_line(self):
        po_line_obj = self.env['purchase.order.line'] 
        if self.is_set :
            bom_env = self.env['mrp.bom']
            pro_bom = bom_env.search([('product_id', '=', self.product_id.id),('set_default','=',True)])
            if pro_bom:
                for bom_line in pro_bom.bom_line_ids:
                    values = {
                        'order_id': self._context.get('active_id'),
                        'product_id': bom_line.product_id.id,
                        'name': self.product_id.full_name,
                        'product_qty': float(bom_line.product_qty * self.quantity_to_add),
                        'price_unit': bom_line.product_id.lst_price,
                        'product_uom' : bom_line.product_id.uom_id.id,
                        'name':bom_line.product_id.name
                             }

                    po_line = po_line_obj.with_context({'trigger_onchange': True,
                                     'onchange_fields_to_trigger': ['product_id', 'product_qty']
                                                    }).create(values)
            if not pro_bom:
                pro_bom = bom_env.search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),('set_default','=',True)])
                if pro_bom:
                    if pro_bom.bom_line_ids:
                        for bom_line in pro_bom.bom_line_ids:
                            values = {}
                            if bom_line.attribute_value_ids:
                                pro_attr = self.product_id.attribute_value_ids.ids
                                bom_attr = bom_line.attribute_value_ids.ids 
                                if list(set(pro_attr).intersection(bom_attr)):
                                    values = {
                                        'order_id': self._context.get('active_id'),
                                        'product_id': bom_line.product_id.id,
                                        'name': self.product_id.full_name,
                                        'product_qty': float(bom_line.product_qty * self.quantity_to_add),
                                        'price_unit': bom_line.product_id.lst_price,
                                        'product_uom' : bom_line.product_id.uom_id.id,
                                        'name':bom_line.product_id.full_name
                                        } 
                                else:
                                    continue  
                            else:
                                values = {
                                    'order_id': self._context.get('active_id'),
                                    'product_id': bom_line.product_id.id,
                                    'name': self.product_id.full_name,
                                    'product_qty': float(bom_line.product_qty * self.quantity_to_add),
                                    'price_unit': bom_line.product_id.lst_price,
                                    'product_uom' : bom_line.product_id.uom_id.id,
                                    'name':bom_line.product_id.full_name
                                        }        
                            po_line = po_line_obj.with_context({'trigger_onchange': True,
                                         'onchange_fields_to_trigger': ['product_id', 'product_qty']
                                                        }).create(values)
                    else:
                        raise UserError(_('No BOM Lines found for the Product.'))
                else:
                    raise UserError(_('No BOM found for the Kit.'))

        if self.is_bundle :
            bundle = {
                        'order_id': self._context.get('active_id'),
                        'product_id': self.product_id.id,
                        'name': self.product_id.full_name,
                        'product_qty': self.quantity_to_add, 
                        'product_uom' : self.product_id.uom_id.id,
                        'price_unit': self.product_id.lst_price,
                        'is_bundle':True,
                        'is_bundle_item':True
                    }
                #line.write({'product_uom_qty': float(line.product_uom_qty * self.quantity_to_add)})            
            bundel_line_id = po_line_obj.with_context({'trigger_onchange': True,
                                     'onchange_fields_to_trigger': ['product_id', 'product_qty']
                                                    }).create(bundle)
            bom_env = self.env['mrp.bom']
            pro_bom = bom_env.search([('product_id', '=', self.product_id.id),('set_default','=',True)])
            if pro_bom:
                for bom_line in pro_bom.bom_line_ids:
                    values = {
                        'order_id': self._context.get('active_id'),
                        'product_id': bom_line.product_id.id,
                        'name': self.product_id.full_name,
                        'product_qty': float(bom_line.product_qty * self.quantity_to_add),
                        'price_unit': bom_line.product_id.lst_price,
                        'product_uom' : bom_line.product_id.uom_id.id,
                        'name':bom_line.product_id.name
                             }

                    po_line = po_line_obj.with_context({'trigger_onchange': True,
                                     'onchange_fields_to_trigger': ['product_id', 'product_uom_qty']
                                                    }).create(values)
            if not pro_bom:
                pro_bom = bom_env.search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),('set_default','=',True)])
                if pro_bom:
                    for bom_line in pro_bom.bom_line_ids:
                        values = {}
                        if bom_line.attribute_value_ids:
                            pro_attr = self.product_id.attribute_value_ids.ids
                            bom_attr = bom_line.attribute_value_ids.ids 
                            if list(set(pro_attr).intersection(bom_attr)):
                                 values = {
                                     'order_id': self._context.get('active_id'),
                                     'product_id': bom_line.product_id.id,
                                     'name': self.product_id.full_name,
                                     'product_qty': float(bom_line.product_qty * self.quantity_to_add),
                                     'price_unit': bom_line.product_id.lst_price,
                                     'product_uom' : bom_line.product_id.uom_id.id,
                                     'name':bom_line.product_id.name
                                    } 
                            else:
                                continue  
                        else:
                            values = {
                                'order_id': self._context.get('active_id'),
                                'product_id': bom_line.product_id.id,
                                'name': self.product_id.full_name,
                                'product_qty': float(bom_line.product_qty * self.quantity_to_add),
                                'price_unit': bom_line.product_id.lst_price,
                                'product_uom' : bom_line.product_id.uom_id.id,
                                'name':bom_line.product_id.name
                                    }        
                        po_line = po_line_obj.with_context({'trigger_onchange': True,
                                     'onchange_fields_to_trigger': ['product_id', 'product_uom_qty']
                                                    }).create(values)
            selected_lines = self.env['purchase.order.line'].search([('id','in',self._context.get('purchase_order_line'))])
            bundle_cost = bundel_line_id.price_unit 
            seq = bundel_line_id.sequence
            
            for line_selected in selected_lines:
                seq = seq +1
                bundle_cost += line_selected.price_unit
                selected_lines.write({'bundle_id':po_line.product_id.id,
                                  'is_bundle_item':True,
                                  'price_tax': 0.0,
                                  'price_total': 0.0,
                                  'price_subtotal': 0.0,
                                  'sequence':seq,})
            if self.is_bundle:  
                vals = {'price_unit':bundle_cost}
                bundel_line_id.write(vals)
            order_id = self.env['purchase.order'].browse(self._context.get('active_id'))
            order_id.write({'update_price':True})
        return True
