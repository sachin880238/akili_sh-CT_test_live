# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    wizard_cart = fields.Boolean("Wizard Cart", default=True)
    wizard_address = fields.Boolean("Wizard Address")
    wizard_details = fields.Boolean("Wizard Details")
    wizard_reviews = fields.Boolean("Wizard Reviews")
    wizard_confirm = fields.Boolean("Wizard Confirm")
    disabled_wizard = fields.Boolean("Wizard Disabled")
