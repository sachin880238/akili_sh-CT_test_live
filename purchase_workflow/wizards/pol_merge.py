from odoo import api, fields, models, _

class PolMerge(models.TransientModel):
    _name = "pol.merge"
    _description = "Purchase order line Merge"

    latest_date = fields.Datetime(string='Date')
    carrier_id = fields.Many2one('delivery.carrier',string='Via')
    route_id = fields.Many2one('stock.location.route',string='Route')


    @api.multi
    def po_merge_lines(self):
        po_line_ids = self.env['purchase.order.line'].browse(self._context.get('o2m_selection').get('order_line').get('ids'))
        quantity = 0
        for line in po_line_ids:
            quantity += line.product_qty

        purchase_order = self.env['purchase.order'].browse(self.env.context.get('active_id'))
        for line in po_line_ids:
            self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'name': line.product_id.full_name,
                'product_id': line.product_id.id,
                'product_qty': quantity,
                'route_id': self.route_id.id,
                'carrier_id': self.carrier_id.id,
                'date_planned': self.latest_date,
                'price_unit': line.product_id.lst_price,
                'product_uom' : line.product_id.uom_id.id
            })
            break
        po_line_ids.unlink()