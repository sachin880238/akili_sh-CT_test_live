# -*- coding: utf-8 -*-
# Copyright 2015-16 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_new_transfer(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if partner.credit_hold:
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit Hold:'))
        return super(StockPicking, self).do_new_transfer()

    @api.multi
    def force_assign(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if partner.credit_hold:
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit Hold:'))
        return super(StockPicking, self).force_assign()

    @api.multi
    def action_confirm(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if partner.credit_hold:
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit Hold:'))
        return super(StockPicking, self).action_confirm()

    @api.multi
    def action_assign(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if partner.credit_hold:
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit Hold:'))
        return super(StockPicking, self).action_assign()
