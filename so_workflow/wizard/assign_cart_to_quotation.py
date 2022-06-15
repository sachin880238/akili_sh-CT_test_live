from odoo import api, fields, models
# import base64

class Convertcart2quotation(models.TransientModel):
    _name = "convert.cart.quotation"
    _description = 'Convert cart to Quotation'

    team_id = fields.Many2one('crm.team', string="Team")
    user_id = fields.Many2one('res.users', string="Salesperson", default=lambda self: self.env.user)

    @api.multi
    def action_convert_cart_to_quotation(self):
        self.ensure_one()
        temp = self.env['sale.order'].search([('id', '=', self._context['active_id'])])
        for rec in temp:
            # pdf, _ = rec.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([rec.id])
            rec.write({'state': 'sent', 'is_cart_saved': False, 'sent_cart': False, 'cart_state': 'quote'})
            # rec.write({'state': 'sent', 'is_cart_saved': False, 'sent_cart': False, 'cart_state': 'quote', 'so_pdf': base64.encodestring(pdf)})
