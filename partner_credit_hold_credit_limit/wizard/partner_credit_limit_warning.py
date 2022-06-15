# -*- coding: utf-8 -*-
# Copyright 2015-16 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _


class PartnerCreditLimit(models.TransientModel):
    _name = 'partner.credit.limit.warning'
    _description = 'Partner Credit Limit Warning'

    message = fields.Char(readonly=True)
