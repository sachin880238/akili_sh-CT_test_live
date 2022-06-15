import time

from odoo import api, fields, models, _



class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for order in sale_orders:
            order.sub_state3 = 'done'
            if order.picking_ids:
                not_done_picks = order.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
                if not_done_picks:
                    order.sub_state3 = 'pack'
                    order.authorized = False
                order._get_pick_pack_ready_status()
        return res     
