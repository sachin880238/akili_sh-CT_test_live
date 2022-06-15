from datetime import datetime
from datetime import timedelta 
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import RedirectWarning
from odoo.tools.float_utils import float_compare


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    #----------PURCHASE THREE STEP ROUTE---------------

    @api.depends('order_line.move_ids.picking_id')
    def _compute_picking(self):
        for order in self:
            pickings = order.order_line.mapped('move_ids.picking_id')
            order.picking_ids = pickings
            order.picking_count = len(pickings)

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        if self.order_line:
            for line in self.order_line:
                if line.route_id:
                    return line.route_id.stock_location_id.id
        elif self.dest_address_id:
            return self.dest_address_id.property_stock_customer.id
        return self.picking_type_id.default_location_dest_id.id

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            picking = None
            for line in order.order_line:
                if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                    pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    #pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.id == line.route_id.stock_location_id.id)
                    if not pickings:
                        res = order._prepare_picking()
                        ## Temprory Hold on route 
                        #if line.route_id:
                        if True:
                            #res['location_dest_id'] = line.route_id.stock_location_id.id
                            picking = StockPicking.create(res)
                    else:
                        picking = pickings[0]
                    moves = line._create_stock_moves(picking)
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                        values={'self': picking, 'origin': order},
                        subtype_id=self.env.ref('mail.mt_note').id)
        return True
