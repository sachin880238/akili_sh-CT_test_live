from odoo import models, fields, api

class SaleQuotation(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_view_documents(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['domain'] = [('res_id', '=', self.id), ('res_model', '=', 'sale.order')]
        action['context'] = {'create': False, 'edit': False, 'delete': False}
        if self.doc_count == 1:
            form_view = [(self.env.ref('base.view_attachment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            documents = self.env['ir.attachment'].search(action['domain'])
            action['res_id'] = documents.id
        elif self.doc_count > 1:
            action.update({'view_mode': 'tree,kanban,form', 'views': [(False, 'tree'), (False, 'kanban'), (False, 'form')]})
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
