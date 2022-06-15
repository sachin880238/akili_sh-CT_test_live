# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
# Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cleared_bank_account = fields.Boolean(string='Cleared? ',
                                          help='Check if the transaction '
                                               'has cleared from the bank')
    bank_acc_rec_statement_id = fields.Many2one('bank.acc.rec.statement',
                                                string='Bank Acc Rec '
                                                       'Statement',
                                                help="The Bank Acc Rec"
                                                     " Statement linked with "
                                                     "the journal item")
    draft_assigned_to_statement = fields.Boolean(string='Assigned to '
                                                        'Statement? ',
                                                 help='Check if the move line'
                                                      ' is assigned to '
                                                      'statement lines')

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    _order = 'sequence'
    sequence = fields.Integer(string="Sequence")

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_account_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_account_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
