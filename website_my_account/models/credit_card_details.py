from odoo import models, api, _, fields
from datetime import datetime
from odoo.exceptions import ValidationError
import time


class Credit_card_details(models.Model):
    _name = "credit.card.detail"
    _description = "Credit Card Detail"

    @api.depends('month','year')
    def get_card_expiry_date(self):
        for rec in self:
            if rec.month and rec.year:
                rec.card_expiry_date = rec.month+'/'+rec.year

    partner_id = fields.Many2one('res.partner','Card Holder')
    debit_card_no = fields.Char('Credit Card Number')
    debit_card_no_encrypt = fields.Char('Credit Card Number encrypt')
    month = fields.Selection([
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12')
    ], required=True, string='Month')
    year = fields.Char(size=4, string='Year', required=True)
    card_holder_name = fields.Char(size=4, string='Card Holder Name', required=True)
    card_expiry_date = fields.Char('Card expiry Date', compute=get_card_expiry_date)

    @api.constrains('year')
    def check_year(self):
        if self.year:
            if not self.year.isdigit():
                raise ValidationError(_("Please insert a valid Year 123"))
            is_valid_year = '%d' % (int(self.year))
            try:
                time.strptime(is_valid_year, '%Y')
            except ValueError:
                raise ValidationError(_("Please insert a valid Year 123"))


class Res_partner(models.Model):
    _inherit="res.partner"


    partner_card_detail_ids = fields.One2many('credit.card.detail', 'partner_id','Credit or Debit Card')
