# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api,_


class HelpWizard(models.TransientModel):
    _name = "erp.help.wizard"
    _description = 'Erp Help Wizard'
    
    name = fields.Char(
        string='Name',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=True
    )

    have_action = fields.Boolean(
        string='Have action',
        required=False,
        readonly=False,
        index=False,
        default=True,
        help=False
    )
    erp_help_id = fields.Many2one(
        string='Help menu',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='erp.help',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    description = fields.Html('Description')
    child_help = fields.Boolean("Child Help")
    is_created = fields.Boolean(
        string='Is not created',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    @api.multi
    def create_help(self):
        url_dict = self._context.get('url_dict')
        res = False
        if url_dict.get('view_type') and url_dict.get('model'):
            model = self.env['ir.model'].search([('model','=',url_dict.get('model'))])
            action_window = self.env['ir.actions.act_window'].browse(url_dict.get('action'))
            
            action_ctx = dict(self.env.context,default_action_window=action_window.id,
                default_action_type= 'ir.actions.act_window',
                default_description= '')

            if model:
                action_ctx['default_model_id'] = model.id

            view_id = self.env.ref('system_app.help_view_form').id
            res =  {
                'name': _('Help'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'erp.help',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'context': action_ctx}
        else:
            if url_dict.get('action'):
                action = self.env['ir.actions.actions'].browse(url_dict.get('action'))
                action_type = action.type
                view_id = self.env.ref('system_app.help_view_form').id
                action_ctx = dict(self.env.context,default_action_action=action.id,
                default_action_type= action_type,
                default_description= '')


                res =  {
                    'name': _('Help'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'erp.help',
                    'views': [(view_id, 'form')],
                    'view_id': view_id,
                    'target': 'new',
                    'context': action_ctx
                }
        return res

    
    @api.multi
    def update_help(self):
        view_id = self.env.ref('system_app.help_view_wizard').id
        return {
                'name': _('Help'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_id':self.erp_help_id.id,
                'view_mode': 'form',
                'res_model': 'erp.help',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'target': 'new',
            }

    @api.multi
    def close_help(self):
        return {'type': 'ir.actions.act_window_close'}
