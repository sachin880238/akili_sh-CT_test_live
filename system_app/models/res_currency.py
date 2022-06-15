# -*- coding: utf-8 -*-
from odoo import fields, models, api
from forex_python.converter import CurrencyRates
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class Currency(models.Model):
    _inherit = "res.currency"
    _description = "Currency"
    _order = "sequence"

    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('active', 'ACTIVE'),
        ('inactive', 'INACTIVE')], default='active')
    sequence = fields.Integer(string='sequence', help="Gives the sequence order when displaying a list of Currencies.")
    unit = fields.Float(string='Unit')
    reference = fields.Char(string='Reference')
    ref_unit = fields.Integer(string='Reference Unit')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_currency_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_currency_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    @api.onchange('currency_unit_label')
    def onchange_unit_label(self):
        self.name = self.currency_unit_label

    def activate_currency(self):
        self.state = 'active'
        self.active = True

    def deactivate_currency(self):
        self.state = 'inactive'
        self.active = False

    def reset_to_draft(self):
        self.state = 'draft'
        self.active = False


class Currencies(models.Model):
    _inherit = "res.currency.rate"

    @api.model
    def _scheduled_update(self):
        cr = CurrencyRates()
        companies = self.env['res.company'].search([])
        self.search([]).unlink()
        try:
            for company in companies:
                rates = cr.get_rates(company.currency_id.name)
                for cur_rate in rates:
                    currency = self.env['res.currency'].search([('name', '=', cur_rate)])
                    if currency:
                        values = {"name": date.today(), "rate": rates[cur_rate], "company_id": company.id, "currency_id": currency.id}
                        self.create(values)
        except:
            _logger.warning("Currency Rates Source Not Ready")
