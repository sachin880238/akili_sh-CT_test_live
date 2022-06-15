from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                lines_with_route = order.order_line.filtered(lambda line: line.route_id)
                lines_without_route = order.order_line.filtered(lambda line: not line.route_id)
                if not pickings:
                    if lines_with_route:
                        picking_types = {line.picking_type_id for line in lines_with_route}
                        for picking_type in picking_types:
                            res = order._prepare_picking()
                            res.update({'picking_type_id': picking_type.id, 'location_dest_id': picking_type.default_location_dest_id.id})
                            picking = StockPicking.create(res)
                            order_lines = lines_with_route.filtered(lambda line: line.picking_type_id == picking_type)
                            moves = order_lines._create_stock_moves(picking)
                            moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                            seq = 0
                            for move in sorted(moves, key=lambda move: move.date_expected):
                                seq += 5
                                move.sequence = seq
                            moves._action_assign()
                            picking.message_post_with_view('mail.message_origin_link',
                                values={'self': picking, 'origin': order},
                                subtype_id=self.env.ref('mail.mt_note').id)
                    if lines_without_route:
                        res = order._prepare_picking()
                        picking = StockPicking.create(res)
                        moves = lines_without_route._create_stock_moves(picking)
                        moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                        seq = 0
                        for move in sorted(moves, key=lambda move: move.date_expected):
                            seq += 5
                            move.sequence = seq
                        moves._action_assign()
                        picking.message_post_with_view('mail.message_origin_link',
                            values={'self': picking, 'origin': order},
                            subtype_id=self.env.ref('mail.mt_note').id)
                else:
                    lines_without_picking_type = order.order_line.filtered(lambda line: not line.picking_type_id)
                    for picking in pickings:
                        lines_with_picking_type = order.order_line.filtered(lambda line: line.picking_type_id == picking.picking_type_id)
                        if lines_with_picking_type:
                            moves = lines_with_picking_type._create_stock_moves(picking)
                        else:
                            moves = lines_without_picking_type._create_stock_moves(picking)
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

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('purchase_selectable', '=', True)], ondelete='restrict')
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To')

    @api.constrains('route_id', 'picking_type_id')
    def _check_route_picking_type_id(self):
        if self.route_id:
            if not self.picking_type_id:
                raise UserError(_("Picking Type is Missing"))
        if self.picking_type_id:
            if not self.route_id:
                raise UserError(_("Route is Missing"))

    @api.multi
    def _create_or_update_picking(self):
        for line in self:
            if line.product_id.type in ('product', 'consu'):
                # Prevent decreasing below received quantity
                if float_compare(line.product_qty, line.qty_received, line.product_uom.rounding) < 0:
                    raise UserError(_('You cannot decrease the ordered quantity below the received quantity.\n'
                                      'Create a return first.'))

                if float_compare(line.product_qty, line.qty_invoiced, line.product_uom.rounding) == -1:
                    # If the quantity is now below the invoiced quantity, create an activity on the vendor bill
                    # inviting the user to create a refund.
                    activity = self.env['mail.activity'].sudo().create({
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'note': _('The quantities on your purchase order indicate less than billed. You should ask for a refund. '),
                        'res_id': line.invoice_lines[0].invoice_id.id,
                        'res_model_id': self.env.ref('account.model_account_invoice').id,
                    })
                    activity._onchange_activity_type_id()

                # If the user increased quantity of existing line or created a new line
                if line.picking_type_id:
                    pickings = line.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.usage in ('internal', 'transit', 'customer') and x.picking_type_id == line.picking_type_id)
                else:
                    pickings = line.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.usage in ('internal', 'transit', 'customer'))
                picking = pickings and pickings[0] or False
                if not picking:
                    res = line.order_id._prepare_picking()
                    if line.picking_type_id:
                        res.update({'picking_type_id': line.picking_type_id.id, 'location_dest_id': line.picking_type_id.default_location_dest_id.id})
                    picking = self.env['stock.picking'].create(res)
                move_vals = line._prepare_stock_moves(picking)
                for move_val in move_vals:
                    self.env['stock.move']\
                        .create(move_val)\
                        ._action_confirm()\
                        ._action_assign()

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        price_unit = self._get_stock_move_price_unit()
        qty = self._get_qty_procurement()
        routes = [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids]
        template = {
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, routes)] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }

        if self.route_id and self.picking_type_id:
            routes.insert(0, self.route_id.id)
            template.update({'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, routes)] or [],
                             'picking_type_id': self.picking_type_id.id,
                             'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                             })

        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            # Always call '_compute_quantity' to round the diff_quantity. Indeed, the PO quantity
            # is not rounded automatically following the UoM.
            if get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = self.product_uom._compute_quantity(diff_quantity, self.product_uom, rounding_method='HALF-UP')
            res.append(template)
        return res
