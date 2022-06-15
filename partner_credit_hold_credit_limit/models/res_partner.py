# -*- coding: utf-8 -*-
# Copyright 2015-16 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_total_credit_used(self):
        for partner in self:
            partner = partner.commercial_partner_id
            child_ids = self.search([('id', 'child_of', partner.id)]).ids
            order_ids = self.env['sale.order'].search(
                [('partner_id', 'in', child_ids), ('state', '=', 'sale')])
            confirmed_so_not_invoiced = 0.0
            for order in order_ids:
                for order_line in order.order_line:
                    if order_line.invoice_status != "invoiced":
                        confirmed_so_not_invoiced += order_line.price_total

            draft_invoices_ids = self.env['account.invoice'].search(
                [('partner_id', 'in', child_ids), ('state', '=', 'draft')])
            draft_invoices_amount = 0.0
            for invoice in draft_invoices_ids:
                draft_invoices_amount += invoice.amount_total

            partner.total_credit_used = partner.credit + \
                confirmed_so_not_invoiced + draft_invoices_amount

    total_credit_used = fields.Monetary(
        compute='_get_total_credit_used',
        string='Total Credit Used',
        help='Total credit used by the partner')
    credit_hold = fields.Boolean(
        string='Credit Hold',
        help='True, if the credit is on hold',
        copy=False)
