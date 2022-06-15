from odoo import models, fields, api

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	
	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		pick_id = None
		values = {}
		product_lines = {}
		stock_picking_env = self.env['stock.picking']
		for line in self.order_line:
			product_lines = {
			'partner_id': self.partner_id.id,
			'product_id':line.product_id.id,
			'product_uom_qty': line.product_uom_qty,
			'name':line.product_id.name,
			'product_uom':line.product_id.uom_id.id,
			}
			for rule in line.route_id:
				for rec in rule.rule_ids:
					values={
						'partner_id':line.partner_id.id,
						'parent_id': line.partner_id.id,
						'location_id':rec.location_src_id.id,
						'location_dest_id':rec.location_id.id,
						'picking_type_id' : rec.picking_type_id.id,
						'origin' : self.cart_name,
						'move_ids_without_package':[(0,0,product_lines)]
					}
					stock_picking_env.create(values)
		return res