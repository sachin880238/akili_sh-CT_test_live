from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)



class ApprovedBy(models.TransientModel):
    _name = "approved.by"
    _description = 'Approved By'

    @api.depends('action')
    def find_match(self):
        rec = self.env['sale.order'].browse(self._context['active_id'])
        self.amount_total = rec.amount_total
        self.customer_id = rec.partner_id
        self.currency_id = rec.currency_id
        return True

    currency_id = fields.Many2one('res.currency', compute='find_match', string='Currency')
    action = fields.Selection([('customer', 'Customer'), ('user', 'Staff')], default='customer', string='Accepted By')
    amount_total = fields.Float(compute='find_match', string='Price')
    hold_lastval = fields.Float(string='Accepted')
    contact_id = fields.Many2one('res.partner', string='Name')
    customer_id = fields.Many2one('res.partner', compute='find_match')
    user_id = fields.Many2one('res.users', string='Contacts')
    reason = fields.Text("Reason")
    new_approve = fields.Float("New")
    reserve_stock = fields.Boolean("Reserve Stock")

    @api.multi
    def action_apply(self):
        pick_id = None
        if self.action == 'customer':
            approved_by = self.contact_id.name
        else:
            approved_by = self.user_id.name
        so_id = self.env['sale.order'].browse(self._context['active_id'])
        val = {'approved_by':approved_by, 'hold_lastval':self.new_approve,'so_authorized': so_id.so_authorized + self.new_approve}
        if self.action != 'customer':
            val['reason_approve'] = self.reason
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        if active_model == 'sale.order':
            sales = self.env['sale.order'].browse(active_ids)
            line_ids = [line.id for sale in sales for line in sale.order_line]
        reserve_loc = self.env['stock.location'].search([('is_loc_reservable','=',True)])
        if self.reserve_stock and so_id.stock_reserved == False:
            for line in so_id.order_line:
                location = self.env['stock.warehouse'].search([],limit=1)
                picking_type_id = self.env['stock.picking.type'].search([('name','=','Reserve Stock Transfers')])
                move_id = self.env['stock.move'].create({
                    'location_id':location.lot_stock_id.id,
                    'location_dest_id':reserve_loc.id,
                    'product_uom_qty':line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'name': u"%s (%s)" % (line.order_id.name, line.name),
                    'sale_line_id': line.id,
                    'res_stock_so_id' : line.id,
                    'picking_type_id' : picking_type_id.id,
                    })
                reserve = move_id._assign_picking()
                pick_id = move_id.picking_id
            pick_confirm = pick_id.action_confirm()
            pick_assign = pick_id.action_assign()
            for line in pick_id.move_ids_without_package:
                if line.reserved_availability < line.product_uom_qty:
                    line.quantity_done = line.product_uom_qty
            
            pick_res = pick_id.button_validate()
            if pick_res:
                wiz = self.env['stock.immediate.transfer'].search([('id', '=',pick_res['res_id'])])
                wiz.process()
            val['stock_reserved'] =True
        so_id.write(val)
        return True