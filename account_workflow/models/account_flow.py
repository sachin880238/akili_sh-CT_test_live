from datetime import datetime
from datetime import timedelta 
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):

    _inherit = "res.partner"

    last_order_date = fields.Date(string='Last Order Date')
    state = fields.Selection([
        ('prospect', 'PROSPECT'),
        ('customer', 'CUSTOMER'),
        ('inactive','INACTIVE')
        ], default='prospect')
    
    @api.one
    def _get_company_currency(self):
        values = super(Partner, self)._get_company_currency()
        if self.customer:
            self.currency_id = self.sal_currency_id
        if self.supplier:
            self.currency_id = self.pur_currency_id
        return values

    @api.multi
    def assign(self):
         self.state = 'customer'
         self.vendor_state = 'vendor'

    @api.multi
    def deactivate(self):
        self.state = 'inactive'
        self.vendor_state = 'inactive'
         

    @api.multi
    def activate(self):
        if self.order_count > 0:
            self.vendor_state = 'vendor'
            self.state = 'customer'
        elif self.quotation_count > 0:
            self.state = 'customer'
            self.vendor_state = 'vendor'
        else:
            self.state = 'prospect'
            self.vendor_state = 'prospect'

    @api.multi
    def deactivate_sale_order(self):
        if self.customer:
            setting = self.env['ir.config_parameter'].search([('key','=','account_workflow.active_customer_days')])
            custom_setting = int(setting.value)
            last_date = datetime.today().date() - timedelta(days=custom_setting) 
            active_cust_ids = self.search([('state','=','customer'),('last_order_date','<=',last_date),('state','!=','inactive')])
            active_cust_ids.write({"state":'inactive'})
        if self.supplier:
            setting = self.env['ir.config_parameter'].search([('key','=','account_workflow.active_vendor_days')])
            custom_setting = int(setting.value)
            last_date = datetime.today().date() - timedelta(days=custom_setting) 
            active_vendor_ids = self.search([('vendor_state','=','vendor'),('last_order_date','<=',last_date),('vendor_state','!=','inactive')])
            active_vendor_ids.write({"vendor_state":'inactive'})

    def has_required_fields(self):
        if self._context['is_customer']:
            action = self.env.ref('account_workflow.sale_action_quotations_customer').read()[0]
        elif not self._context['is_customer']:
            action = self.env.ref('account_workflow.purchase_action_quotations_customer').read()[0]
        if self.email or self.phone:
            return action
        else:
            raise ValidationError(_('Please provide either email or telephone.'))

    @api.multi
    def get_opportunity_view(self):
        if self.opportunity_count > 0:
            action = self.env.ref('account_workflow.customer_opportunities_tree').read()[0]
            return action
        else:
            tree_view = self.env.ref('lead_process.crm_opportunity_tree_view')
            form_view = self.env.ref('crm.crm_case_form_view_oppor')
            kanban_view = self.env.ref('lead_process.crm_opportunity_kanban_view')
            graph_view = self.env.ref('crm.crm_lead_view_graph')
            pivot_view = self.env.ref('crm.crm_lead_view_pivot')
            calendar_view = self.env.ref('crm.crm_case_calendar_view_leads')
            return {
                'name': _('Opportunities'),
                'view_type': 'form',
                'res_model': 'crm.lead',
                'views': [
                            (tree_view.id,'tree'), (form_view.id,'form'), (kanban_view.id,'kanban'),
                            (graph_view.id,'graph'), (pivot_view.id,'pivot'), (calendar_view.id,'calendar')
                        ],
                'context': {'default_type': 'opportunity'},
                'domain': [('partner_id', '=', self._context.get('active_id', False)),('type','=','opportunity')],
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self,vals):
        record = super(SaleOrder, self).create(vals)
        if record.partner_id.state != 'customer':
            record.partner_id.write({'state':'customer'})
        record.partner_id.write({'last_order_date': record.date_order})
        return record