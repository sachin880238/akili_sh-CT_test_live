from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence")
    cart_line = fields.One2many('sale.cart.line', 'cart_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    state = fields.Selection([
        ('draft', 'CART'),
        ('sent', 'QUOTATION'),
        ('order', 'ORDER'),
        ('sale', 'SALE'),
        ('done', 'LOCKED'),
        ('cancel', 'CANCEL')], string='Stage', readonly=True, copy=False, index=True, track_visibility='onchange')
    cart_state = fields.Selection(
        [('active', 'ACTIVE'),
         ('saved', 'SAVED'),
         ('rfq', 'RFQ'),
         ('quote', 'QUOTATION'),
         ('cancel', 'CANCEL')], default='active', track_visibility='onchange', readonly=True, copy=False, string="Stage")
    is_cart_saved = fields.Boolean("Saved Cart")
    sent_cart = fields.Boolean(string="RFQ")
    cart_name = fields.Char(compute='get_cart_name')
    payment_count = fields.Integer(string='Payments')
    card_count = fields.Integer(string='Cards')
    doc_count = fields.Integer(string='Documents', compute="_compute_documents")
    cart_amount_untaxed = fields.Monetary(string="Products", compute='_cart_amount_all')
    cart_amount_tax = fields.Monetary(string="Service Tax", compute='_cart_amount_all')
    cart_amount_total = fields.Monetary(string="Total", compute='_cart_amount_all')

    def _compute_documents(self):
        for record in self:
            documents = record.env['ir.attachment'].search([('res_id', '=', record.id), ('res_model', '=', 'sale.order')])
            record.doc_count = len(documents)

    @api.depends('order_line.price_total')
    def _cart_amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.cart_line:
                amount_untaxed += line.net_price
                amount_tax += line.price_tax
            order.update({
                'cart_amount_untaxed': amount_untaxed,
                'cart_amount_tax': amount_tax,
                'cart_amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('name', 'partner_id')
    def get_cart_name(self):
        for rec in self:
            # if rec.state in ['order','sale','done']:
            #     cart_name = str(rec.name)
            #     sale_cart_name = cart_name.replace('Q','O')
            #     rec.name = sale_cart_name

            if rec.name and rec.partner_id.name:
                if rec.name == 'New':
                    rec.cart_name = rec.partner_id.name
                else:
                    rec.cart_name = rec.name + ' ' + rec.partner_id.name

    @api.multi
    def action_view_cards(self):
        return True

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.state == 'draft':
                for rec in self:
                    if rec.partner_id:
                        res.append((rec.id, '%s' % (rec.partner_id.name)))
                        return res
        return super(SaleOrder, self).name_get()

    @api.multi
    def action_quotation_cart(self):
        self.ensure_one()
        for rec in self:
            cart_line = []
            for line in rec.order_line:
                val = {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'discount': line.discount,
                    'price_unit': line.price_unit,
                    'product_uom': line.product_uom.id,
                    'cart_id': line.order_id.id,
                    'price_subtotal': line.product_uom_qty * line.price_unit
                }
                cart_line.append((0, 0, val))
            self.write({'state': 'sent', 'is_cart_saved': False, 'sent_cart': False, 'cart_line': cart_line})

    @api.multi
    def action_quotation_cart_send(self):
        return True

    @api.multi
    def action_view_payments(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        result = super(SaleOrderLine, self).create(vals)
        if result.order_id.state == 'draft':
            cart_line = self.env['sale.cart.line']
            cart_vals = {
                'name': result.name,
                'cart_id': result.order_id.id,
                'line_id': result.id,
                'product_id': result.product_id.id,
                'product_uom_qty': result.product_uom_qty,
                'product_uom': result.product_uom.id,
                'price_unit': result.price_unit,
                'cart_discount': result.discount,
                'list_price': result.price_unit,
                'net_price': result.price_subtotal,
                'price_tax': result.price_tax,
                'price_reduce_taxinc': result.price_reduce_taxinc,
                'price_reduce_taxexcl': result.price_reduce_taxexcl,
            }
            cart_line.create(cart_vals)
        return result

    @api.multi
    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        if self.order_id.state == 'draft':
            cart_line = self.env['sale.cart.line'].search([('line_id', '=', self.id)])
            if cart_line:
                cart_vals = {
                    'name': self.name,
                    'cart_id': self.order_id.id,
                    'line_id': self.id,
                    'product_id': self.product_id.id,
                    'product_uom_qty': self.product_uom_qty,
                    'product_uom': self.product_uom.id,
                    'price_unit': self.price_unit,
                    'cart_discount': self.discount,
                    'list_price': self.price_unit,
                    'net_price': self.price_subtotal,
                    'price_tax': self.price_tax,
                    'price_reduce_taxinc': self.price_reduce_taxinc,
                    'price_reduce_taxexcl': self.price_reduce_taxexcl,
                }
                cart_line.write(cart_vals)
        return result

    def unlink(self):
        if self.order_id.state == 'draft':
            cart_line = self.env['sale.cart.line'].search([('line_id', '=', self.id)])
            if cart_line:
                cart_line.unlink()
        return super(SaleOrderLine, self).unlink()

class SaleCartLine(models.Model):
    _name = 'sale.cart.line'
    _description = 'Sale Cart Line'

    name = fields.Text(string='Product', compute='compute_product_description')
    cart_id = fields.Many2one('sale.order', string='Order Reference')
    line_id = fields.Many2one('sale.order.line', string='Order Line')
    product_id = fields.Many2one('product.product', string='Product')
    product_description = fields.Text(string='Description', compute='compute_product_description')
    product_uom_qty = fields.Float('Quantity')
    product_uom = fields.Many2one('uom.uom', string='UOM')
    warning_message = fields.Text(string='Warning', compute='compute_product_description')
    list_price = fields.Float('List')
    cart_discount = fields.Float('Disc')
    price_unit = fields.Float('Unit')
    net_price = fields.Float('Net')
    price_tax = fields.Float(string='Tax')
    price_reduce_taxinc = fields.Float(string='Price Reduce Tax inc')
    price_reduce_taxexcl = fields.Float(string='Price Reduce Tax excl')

    def compute_product_description(self):
        for record in self:
            if record.product_id.sale_line_warn_msg:
                record.warning_message = record.product_id.sale_line_warn_msg
            if record.product_id and record.product_id.description_quote:
                record.name = record.product_id.full_name + '\n' + record.product_id.description_quote
                record.product_description = record.product_id.description_quote
            else:
                record.name = record.product_id.full_name
