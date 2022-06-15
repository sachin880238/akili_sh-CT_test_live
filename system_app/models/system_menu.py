# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class HelpMenu(models.Model):
    _name = "erp.help"
    _description = 'Erp Help'
    _order = 'sequence'

    @api.onchange('action_window')
    def get_view_id(self):
        for rec in self:
            if 'url_dict' not in rec._context:
                continue
            v_type = False
            if rec._context['url_dict']['view_type'] == 'list':
                v_type = 'tree'
            else:
                v_type = rec._context['url_dict']['view_type']
            if rec.view_id and rec.view_types:
                continue
            if rec.action_window.view_id:
                rec.view_id = rec.action_window.view_id.id
                rec.view_types = v_type
                continue
            view_id = rec.env['ir.ui.view'].search([('model','=',rec.action_window.res_model),('type','=',v_type)], limit=1)  
            rec.view_id = view_id.ids[0]
            rec.view_types = v_type

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=True
    )

    @api.onchange('action_window')
    def window_name(self):
        self.name = self.action_window.name

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_so_line_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_so_line_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    description = fields.Html(copy=False)

    short_desc = fields.Char(string="Description", copy=False)

    model_id = fields.Many2one('ir.model', string='Model')

    action_window = fields.Many2one('ir.actions.act_window', string='Window')

    act_window = fields.Char(string="Window")

    child_help = fields.Boolean("Child Help")

    parent_action_window = fields.Many2one('ir.actions.act_window', string='Parent Window')

    parent_model_id = fields.Many2one('ir.model', string='Parent Model')

    parent_view_id = fields.Many2one('ir.ui.view', string='View ID')
    code_name = fields.Char()

    res_model = fields.Char(
        string='Res model',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        related='action_window.res_model',
        translate=True
    )

    view_id = fields.Many2one('ir.ui.view', string='View ID')

    view_types = fields.Selection([('tree', 'Tree'),
        ('form', 'Form'),
        ('graph', 'Graph'),
        ('pivot', 'Pivot'),
        ('calendar', 'Calendar'),
        ('diagram', 'Diagram'),
        ('gantt', 'Gantt'),
        ('kanban', 'Kanban'),
        ('search', 'Search'),
        ('qweb', 'QWeb'),
        ('list', 'List')], string='Type')

    action_action = fields.Many2one('ir.actions.actions', string='Action')

    action_type = fields.Selection(
        string='Action type',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[('ir.actions.act_window', 'ir.actions.act_window'), ('ir.actions.client', 'ir.actions.client')])
    state = fields.Selection([('draft', 'DRAFT'), ('published', 'PUBLISHED')], required=True, default='draft', string="Stage")

    def publish_help(self):
        if self.action_window or self.parent_action_window:
            if self.child_help:
                def_rec = self.search([('code_name','=',self.code_name),('model_id','=',self.model_id.id),('view_types','=',self.view_types),('parent_model_id','=',self.parent_model_id.id),('parent_action_window','=',self.parent_action_window.id),('default_type','=',True), ('child_help', '=', True)])
            else:
                def_rec = self.search([('model_id','=',self.model_id.id),('view_types','=',self.view_types),('view_id','=',self.view_id.id),('action_window','=',self.action_window.id),('default_type','=',True)])
        elif self.action_action:
            def_rec = self.search([('model_id', '=', self.model_id.id), ('view_types', '=', self.view_types),('view_id','=',self.view_id.id),('action_action','=',self.action_action.id),('default_type','=',True)])
        if def_rec:
            def_rec.default_type = False
            def_rec.state = 'draft'            
            self.default_type = True
            self.state = 'published'
        else:
            self.default_type = True
            self.state = 'published'

    @api.onchange('default_type')
    def default_field(self):
        if self.action_window or self.parent_action_window:
            if self.child_help:
                def_rec = self.search([('code_name','=',self.code_name),('model_id', '=', self.model_id.id), ('view_types', '=', self.view_types), ('default_type', '=', True), ('child_help', '=', True), ('parent_action_window', '=', self.parent_action_window.id), ('parent_model_id', '=', self.parent_model_id.id)])
            else:
                def_rec = self.search([('model_id','=',self.model_id.id),('view_types','=',self.view_types),('view_id','=',self.view_id.id),('action_window','=',self.action_window.id),('default_type','=',True)])
        elif self.action_action:
            def_rec = self.search([('model_id', '=', self.model_id.id), ('view_types', '=', self.view_types),('view_id','=',self.view_id.id),('action_action','=',self.action_action.id),('default_type','=',True)])
        if def_rec:
            if not self.default_type:
                if 'active_id' not in self._context:
                    self.default_type = True

    default_type = fields.Boolean(string="Default", copy=False)

    @api.model
    def create(self, vals):
        if vals.get('action_window') or vals.get('parent_action_window'):
            if vals.get('child_help'):
                def_record = self.search([('code_name','=',vals['code_name']),('model_id', '=', vals['model_id']), ('view_types', '=', vals['view_types']), ('default_type', '=', True), ('child_help', '=', True), ('parent_model_id', '=', vals['parent_model_id']), ('parent_action_window', '=', vals['parent_action_window'])])
            else:
                def_record = self.search([('model_id', '=', vals['model_id']), ('view_types', '=', vals['view_types']),('view_id','=',vals['view_id']),('action_window','=',vals['action_window']),('default_type','=',True)])
        elif vals.get('action_action'):
            def_record = self.search([('model_id', '=', vals['model_id']), ('view_types', '=', vals['view_types']),('view_id','=',vals['view_id']),('action_action','=',vals['action_action']),('default_type','=',True)])

        if vals.get('default_type', False):
            if def_record.default_type:
                def_record.write({'default_type': False})

        if not vals.get('default_type', False):
            if not def_record:
                vals['default_type'] = True
            if not def_record.default_type:
                vals['default_type'] = True

        res = super(HelpMenu, self).create(vals)
        if res.action_window and res.action_type == 'ir.actions.act_window':
            res.write({'name': res.name})
        if res.action_action and res.action_type == 'ir.actions.client':
            res.write({'name': res.name})
        return res

    @api.multi
    def write(self, vals):
        if vals.get('default_type'):
            if self.action_window or self.parent_action_window:
                if vals.get('child_help') or self.child_help:
                    def_rec = self.search([('code_name','=',self.code_name),('model_id', '=', self.model_id.id), ('view_types', '=', self.view_types), ('child_help', '=', True), ('parent_action_window', '=', self.parent_action_window.id), ('parent_model_id', '=', self.parent_model_id.id)])
                else:
                    def_rec = self.search([('model_id','=',self.model_id.id),('view_types','=',self.view_types),('view_id','=',self.view_id.id),('action_window','=',self.action_window.id)])
            elif self.action_action:
                def_rec = self.search([('model_id','=',self.model_id.id),('view_types','=',self.view_types),('view_id','=',self.view_id.id),('action_action','=',self.action_action.id)])
            for rec in def_rec:
                rec.default_type = False
        
        res = super(HelpMenu, self).write(vals)
        if vals.get('action_window') and self.action_type == 'ir.actions.act_window':
            self.name = self.action_window.name
        if vals.get('action_action') and self.action_type == 'ir.actions.client':
            self.write = self.action_action.name
        return res   
    
    @api.model 
    def fetch_help(self,url_dict={}):
        if url_dict.get('view_type') and url_dict.get('model'):
            if url_dict.get('view_type') == 'list':
                v_type = 'list'
            else:
                v_type = url_dict.get('view_type')
            model = self.env['ir.model'].search([('model','=',url_dict.get('model'))])
            action_window = self.env['ir.actions.act_window'].browse(url_dict.get('action'))
            view_id = action_window.view_id
            helps = self.search([('model_id','=',model.id),('action_window','=',action_window.id),('view_types','=',v_type),('default_type','=',True),('child_help', '=', False)],limit=1)
            if helps:
                help_wizard = self.env['erp.help.wizard'].create({'description': helps.description,'is_created':True, 'erp_help_id':helps.id, 'name': helps.name})
                return {
                    'res_id': help_wizard.id,
                    'action_name':action_window.name,
                    'help_id':helps.id
                }    
            else:
                vals = {}
                vals['res_model'] = url_dict['model']
                vals['action_action'] = False
                vals['state'] = 'published'
                vals['action_window'] = url_dict['action']
                vals['default_type'] = False
                vals['act_window'] = False
                vals['description'] = '<p><br></p>'
                vals['short_desc'] = False
                vals['action_type'] = 'ir.actions.act_window'
                vals['view_types'] = url_dict['view_type']
                vals['model_id'] = model.id
                vals['view_id'] = view_id.id
                vals['name'] = action_window.name + " " + str(url_dict['view_type']).capitalize()
                self.create(vals)
                helps = self.search([('model_id','=',model.id),('action_window','=',action_window.id),('view_types','=',v_type),('default_type','=',True), ('child_help', '=', False)],limit=1)
                help_wizard = self.env['erp.help.wizard'].create({'description': helps.description,'is_created':True, 'erp_help_id':helps.id, 'name': helps.name})
                return {
                    'res_id': help_wizard.id,
                    'action_name':action_window.name,
                    'help_id':helps.id
                    }

        elif url_dict.get('action') and not url_dict.get('view_type') and not url_dict.get('model'):
            action = self.env['ir.actions.actions'].browse(url_dict.get('action'))
            action_type = action.type
            helps = self.search([('action_action','=',action.id),('action_type','=',action_type),('default_type','=',True), ('child_help', '=', False)],limit=1)
           
            if helps:                            
                help_wizard = self.env['erp.help.wizard'].create({'description': helps.description,'is_created':True, 'erp_help_id':helps.id, 'name': helps.name})
                return {
                        'res_id': help_wizard.id,
                        'action_name':action.name,
                        'help_id':helps.id
                    } 
              
            else:
                vals = {}
                vals['res_model'] = False
                vals['action_action'] = action.id
                vals['state'] = 'published'
                vals['action_window'] = False
                vals['default_type'] = False
                vals['act_window'] = False
                vals['description'] = '<p><br></p>'
                vals['short_desc'] = False
                vals['action_type'] = action_type
                vals['view_types'] = False
                vals['model_id'] = False
                vals['view_id'] = False
                vals['name'] = action.name
                self.create(vals)   
                helps = self.search([('name','=',action.name), ('action_window','=',False),('default_type','=',True), ('child_help', '=', False), ('action_type', '=', 'ir.actions.client')],limit=1)
                help_wizard = self.env['erp.help.wizard'].create({'description': helps.description,'is_created':True, 'erp_help_id':helps.id, 'name': helps.name})
                
                return {
                    'res_id': help_wizard.id,
                    'action_name':action.name,
                    'help_id':helps.id
                    }               
        else:
            return {
                    'res_id': False,
                    'action_name':False,
            }


    @api.model
    def fetch_child_rec_help(self, url_dict={}, parent_dict={}):
        if url_dict.get('view_type') and url_dict.get('res_model'):
            v_type = url_dict.get('view_type')
            model = self.env['ir.model'].search([('model', '=', url_dict.get('res_model'))])
            parent_model = self.env['ir.model'].search([('model', '=', parent_dict.get('model'))])
            title = url_dict.get('title')
            helps = self.search([('code_name','=',title),('model_id', '=', model.id), ('child_help', '=', True), ('view_types', '=', v_type), ('default_type', '=', True), ('parent_action_window', '=', parent_dict['action']), ('parent_model_id', '=', parent_model.id)], limit=1)
            
            if helps:
                help_wizard = self.env['erp.help.wizard'].create({'description': helps.description, 'is_created': True, 'erp_help_id': helps.id, 'name': helps.name, 'child_help': True})
                return {
                'res_id': help_wizard.id,
                    'name':helps.name,
                    'desc':helps.short_desc,
                    'action_name':title,
                    'description':helps.description,
                    'help_id':helps.id
                    
                    
                }
            
            else:
                vals = {}
                vals['res_model'] = url_dict['res_model']
                vals['action_action'] = False
                vals['code_name']=title
                vals['state'] = 'published'
                vals['action_window'] = False
                vals['default_type'] = False
                vals['act_window'] = False
                vals['description'] = '<p><br></p>'
                vals['short_desc'] = False
                vals['action_type'] = 'ir.actions.act_window'
                vals['view_types'] = url_dict['view_type']
                vals['model_id'] = model.id
                vals['view_id'] = False
                vals['name'] = title + " " + str(url_dict['view_type']).capitalize()
                vals['child_help'] = True
                vals['parent_action_window'] = parent_dict['action']
                vals['parent_model_id'] = parent_model.id
                self.create(vals)
                helps = self.search([('code_name','=',vals['code_name']),('model_id', '=', model.id), ('child_help', '=', True), ('view_types', '=', v_type), ('default_type', '=', True), ('parent_action_window', '=', parent_dict['action']), ('parent_model_id', '=', parent_model.id)], limit=1)
                help_wizard = self.env['erp.help.wizard'].create({'description': helps.description, 'is_created':True, 'erp_help_id': helps.id, 'name': helps.name, 'child_help': True})
                return {
                    'res_id': help_wizard.id,
                    'name':helps.name,
                    'desc':helps.short_desc,
                    'action_name':title,
                    'description':helps.description,
                    'help_id':helps.id
                    
                }
        else:
            return {
                    'res_id': False,
                    'action_name': False,
            }

    @api.multi
    def duplicate_help(self, default=None):
        res = super(HelpMenu, self).copy(default=default)
        return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'erp.help',
                    'target': 'current',
                    'res_id': res.id,
                    'type': 'ir.actions.act_window'
                    }


    @api.model
    def save_data(self, data_dict={}):
        help_id = self.search([('id','=',int(data_dict['id']))])
        if help_id:
            help_id.write({'description':data_dict['desc'],'name':data_dict['input']})

        return

    @api.multi
    def unlink(self):
        records = [record for record in self if record.default_type]
        if records:
            for rec in records:
                raise ValidationError(_("Please set another help as published to delete %s.") %rec.name)
        else:
            return super(HelpMenu, self).unlink()
