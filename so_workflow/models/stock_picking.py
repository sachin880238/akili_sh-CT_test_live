# from odoo import api, fields, models, _


# class StockMove(models.Model):
#     _inherit = ['stock.move']

#         def _assign_picking(self):
#         """ Try to assign the moves to an existing picking that has not been
#         reserved yet and has the same procurement group, locations and picking
#         type (moves should already have them identical). Otherwise, create a new
#         picking to assign them to. """
#         Picking = self.env['stock.picking']
#         for move in self:
#             recompute = False
#             picking = move._search_picking_for_assignation()
#             if picking:
#                 if picking.partner_id.id != move.partner_id.id or picking.origin != move.origin:
#                     # If a picking is found, we'll append `move` to its move list and thus its
#                     # `partner_id` and `ref` field will refer to multiple records. In this
#                     # case, we chose to  wipe them.
#                     picking.write({
#                         'partner_id': False,
#                         'origin': False,
#                     })
#             else:
#                 recompute = True
#                 picking = Picking.create(move._get_new_picking_values())
#             move.write({'picking_id': picking.id})
#             move._assign_picking_post_process(new=recompute)
#             # If this method is called in batch by a write on a one2many and
#             # at some point had to create a picking, some next iterations could
#             # try to find back the created picking. As we look for it by searching
#             # on some computed fields, we have to force a recompute, else the
#             # record won't be found.
#             if recompute:
#                 move.recompute()
#         return True

# class StockPicking(models.Model):
#     _inherit = "stock.picking"


    # @api.multi
    # def action_assign(self):
    #     # if smove_lelf.move_lines.sale_line_id.order_id.stock_reserved:
    #     #     self.
    #     # self.order
    #     # If a package level is done when confirmed its location can be different than where it will be reserved.
    #     # So we remove the move lines created when confirmed to set quantity done to the new reserved ones.
    #     res = super(StockPicking, self).action_assign()
    #     so_id = self.env['sale.order'].search([('name','=',self.origin)])
    #     return res