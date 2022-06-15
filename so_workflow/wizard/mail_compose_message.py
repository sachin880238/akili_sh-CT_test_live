from odoo import api, fields, models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def action_send_mail(self):
        if self._context.get('active_model') == 'sale.order':
            quotation_id = self.env['sale.order'].search([('id', '=', self._context.get('active_id'))])
            quotation_id.so_pdf = self.attachment_ids.datas
            if quotation_id.cart_line:
                website_line = self.env['sale.cart.line'].search([('line_id', '=', False)])
                for line in website_line:
                    line.unlink()
                for line in quotation_id.order_line:
                    website_line = self.env['sale.cart.line'].search([('line_id', '=', line.id)])
                    if website_line:
                        website_vals = {
                            'name': line.name,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,
                            'price_unit': line.price_unit,
                            'cart_discount': line.discount,
                            'list_price': line.price_unit,
                            'net_price': line.price_subtotal,
                            'price_tax': line.price_tax,
                            'price_reduce_taxinc': line.price_reduce_taxinc,
                            'price_reduce_taxexcl': line.price_reduce_taxexcl,
                        }
                        website_line.write(website_vals)
                    else:
                        website_vals = {
                            'name': line.name,
                            'cart_id': quotation_id.id,
                            'line_id': line.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,
                            'price_unit': line.price_unit,
                            'cart_discount': line.discount,
                            'list_price': line.price_unit,
                            'net_price': line.price_subtotal,
                            'price_tax': line.price_tax,
                            'price_reduce_taxinc': line.price_reduce_taxinc,
                            'price_reduce_taxexcl': line.price_reduce_taxexcl,
                        }
                        website_line.create(website_vals)
            else:
                for line in quotation_id.order_line:
                    website_line = self.env['sale.cart.line']
                    website_vals = {
                        'name': line.name,
                        'cart_id': quotation_id.id,
                        'line_id': line.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'price_unit': line.price_unit,
                        'cart_discount': line.discount,
                        'list_price': line.price_unit,
                        'net_price': line.price_subtotal,
                        'price_tax': line.price_tax,
                        'price_reduce_taxinc': line.price_reduce_taxinc,
                        'price_reduce_taxexcl': line.price_reduce_taxexcl,
                    }
                    website_line.create(website_vals)

            if quotation_id.so_authorized >= quotation_id.amount_total:
                quotation_id.write({'quote_stage': 'order', 'state': 'order', 'mail_sent': True})
            else:
                quotation_id.write({'quote_stage': 'accept', 'mail_sent': True})

        res = super(MailComposer, self).action_send_mail()
        return res
