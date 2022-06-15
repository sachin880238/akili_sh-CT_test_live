from odoo import api, fields, models
from odoo.http import request


class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.multi
    def _compute_last_website_so_id(self):
        SaleOrder = self.env['sale.order']
        for partner in self:
            is_public = any([u._is_public()
                for u in partner.with_context(active_test=False).user_ids])
            if request and hasattr(request, 'website') and not is_public:
                partner.last_website_so_id = SaleOrder.search([
                    ('partner_id', '=', partner.id),
                    ('state','=','draft'),
                    ('team_id.team_type', '=', 'website'),
                    ('website_id', '=', request.website.id),
                    ('is_cart_saved', '=', False),
                    ('sent_cart', '=', False),
                ], order='write_date desc', limit=1)
            else:
                partner.last_website_so_id = SaleOrder


    @api.multi
    def del_att(self):
        att_obj = request.env['ir.attachment']
        attachments = att_obj.sudo().search([('res_model', '=', 'sale.order'), ('res_id', '=', order.id)])
        return attachments