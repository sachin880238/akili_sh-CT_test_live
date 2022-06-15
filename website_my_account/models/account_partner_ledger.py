from odoo import models, api, _, fields
from odoo.tools.misc import formatLang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"


    @api.model
    def _lines_partner(self, partner, line_id=None):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_partners = self.with_context(date_from_aml=context['date_from'], date_from=context['date_from'] and company_id.compute_fiscalyear_dates(datetime.strptime(context['date_from'], DEFAULT_SERVER_DATE_FORMAT))['date_from'] or None).group_by_partner_id(line_id)  # Aml go back to the beginning of the user chosen range but the amount on the partner line should go back to either the beginning of the fy or the beginning of times depending on the partner
        unfold_all = context.get('print_mode') and not context['context_id']['unfolded_partners']
        if grouped_partners.get(partner):
            debit = grouped_partners[partner]['debit']
            credit = grouped_partners[partner]['credit']
            balance = grouped_partners[partner]['balance']
            move_line = grouped_partners[partner]['lines']
            lines.append({
                'id': partner.id,
                'type': 'line',
                'name': partner.name,
                'footnotes': self.env.context['context_id']._get_footnotes('line', partner.id),
                'columns': [self._format(debit), self._format(credit), self._format(balance),move_line],
                'level': 2,
                'unfoldable': True,
                'unfolded': partner in context['context_id']['unfolded_partners'] or unfold_all,
                'colspan': 5,
            })
        if partner in context['context_id']['unfolded_partners'] or unfold_all:
            progress = 0
            domain_lines = []
            amls = amls_all = grouped_partners[partner]['lines']
            too_many = False
            if len(amls) > 80 and not context.get('print_mode'):
                amls = amls[-80:]
                too_many = True
            for line in amls:
                if self.env.context['cash_basis']:
                    line_debit = line.debit_cash_basis
                    line_credit = line.credit_cash_basis
                else:
                    line_debit = line.debit
                    line_credit = line.credit
                progress = progress + line_debit - line_credit
                name = []
                name = '-'.join(
                    line.move_id.name not in ['', '/'] and [line.move_id.name] or [] +
                    line.ref not in ['', '/'] and [line.ref] or [] +
                    line.name not in ['', '/'] and [line.name] or []
                )
                if len(name) > 35 and not self.env.context.get('no_format'):
                    name = name[:32] + "..."
                domain_lines.append({
                    'id': line.id,
                    'type': 'move_line_id',
                    'move_id': line.move_id.id,
                    'action': line.get_model_id_and_name(),
                    'name': line.date,
                    'footnotes': self.env.context['context_id']._get_footnotes('move_line_id', line.id),
                    'columns': [line.journal_id.code, line.account_id.code, name, line.full_reconcile_id.name,
                                line_debit != 0 and self._format(line_debit) or '',
                                line_credit != 0 and self._format(line_credit) or '',
                                self._format(progress)],
                    'level': 1,
                })
            initial_debit = grouped_partners[partner]['initial_bal']['debit']
            initial_credit = grouped_partners[partner]['initial_bal']['credit']
            initial_balance = grouped_partners[partner]['initial_bal']['balance']
            domain_lines[:0] = [{
                'id': partner.id,
                'type': 'initial_balance',
                'name': _('Initial Balance'),
                'footnotes': self.env.context['context_id']._get_footnotes('initial_balance', partner.id),
                'columns': ['', '', '', '', self._format(initial_debit), self._format(initial_credit), self._format(initial_balance)],
                'level': 1,
            }]
            domain_lines.append({
                'id': partner.id,
                'type': 'o_account_reports_domain_total',
                'name': _('Total') + ' ' + partner.name,
                'footnotes': self.env.context['context_id']._get_footnotes('o_account_reports_domain_total', partner.id),
                'columns': ['', '', '', '', self._format(debit), self._format(credit), self._format(balance)],
                'level': 1,
            })
            if too_many:
                domain_lines.append({
                    'id': partner.id,
                    'domain': "[('id', 'in', %s)]" % amls_all.ids,
                    'type': 'too_many_partners',
                    'name': _('There are more than 80 items in this list, click here to see all of them'),
                    'footnotes': {},
                    'colspan': 8,
                    'columns': [],
                    'level': 3,
                })
            lines += domain_lines
        return lines