# -*- coding: utf-8 -*-
# Copyright 2015-16 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _payments_count(self):
        for order in self:
            order.payments_count = self.env['account.payment'].search_count(
                [('partner_id', 'child_of', order.commercial_partner_id.id),
                 ('state', 'in', ['draft', 'posted']),
                 ('invoice_ids', '=', False)])

    payments_count = fields.Integer(compute='_payments_count')
    show_payment_button = fields.Boolean(
        compute='_compute_show_payment_button'
    )
    override_credit_limit = fields.Boolean(
        string='Override Credit Limit',
        copy=False,
    )
    commercial_partner_id = fields.Many2one(
        'res.partner',
        related='partner_id.commercial_partner_id',
        readonly=True,
    )
    payment_method_id = fields.Many2one(
        'account.journal',
        string='Payment Method', copy=False,
    )
    over_credit = fields.Boolean(
        string='Over Credit',
        copy=False,
        readonly=True
    )

    @api.multi
    def _compute_show_payment_button(self):
        for order in self:
            order.show_payment_button = self.env[
                'res.config.settings']._get_add_prepayment_test()

    def check_partner_credit_limit(self):
        prepayment_test = self.env[
            'res.config.settings']._get_add_prepayment_test()
        over_credit_limit = self.env[
            'res.config.settings']._get_over_credit_limit()
        for sale_id in self:
            partner = sale_id.partner_id.commercial_partner_id
            if partner.credit_hold:
                raise UserError(_('Credit Hold!\n\nThis Account is on Hold'))
            if (partner.credit_limit > 0 or prepayment_test) and not sale_id.override_credit_limit:
                if partner.total_credit_used == 0 and partner.credit_limit == 0:
                    continue
                if partner.total_credit_used >= partner.credit_limit and over_credit_limit:
                    raise UserError(
                        _("Credit over Limit!\n\nThis customer has already exceeded his/her credit limit: %s" % (partner.credit_limit)))
                elif sale_id.state != "sale" and partner.total_credit_used + sale_id.amount_total > partner.credit_limit and over_credit_limit:
                    raise UserError(
                        _("Credit over Limit!\n\nThis Sales Order would exceed the credit limit of this customer: %s" % (partner.credit_limit)))

 
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        partner = self.partner_id.commercial_partner_id
        if partner.credit_hold:
            return {'warning': {'title': _("Warning!"), 'message': (
                '\nThis customer Account is on credit hold.\n\n The order would not process until credit hold is released.\n\n')}}
        elif partner.credit_limit > 0 and partner.total_credit_used >= partner.credit_limit and not self.override_credit_limit:
            return {'warning': {'title': _("Warning!"), 'message': (
                '\nThis customer has already exceeded his/her credit limit.\n\n')}}

    @api.multi
    def open_payments(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.update({
            'default_payment_type': 'inbound',
            'default_partner_id': self.partner_id.id,
            'default_journal_id': self.payment_method_id.id,
            'default_amount': self.amount_total,
        })
        action = self.env.ref('account.action_account_payments').read([])[0]
        if action:
            action['context'] = ctx
            action['domain'] = [
                ('partner_id', 'child_of', self.commercial_partner_id.id),
                ('state', 'in', ['draft', 'posted']),
                ('invoice_ids', '=', False)]
            return action
