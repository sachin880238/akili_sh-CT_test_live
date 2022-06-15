from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
import ast
from ast import literal_eval
import csv
import json


class IrAction(models.Model):
        
    _inherit = 'ir.actions.actions'

    @api.multi
    def find_view_id(self):
        record_id = self.env.ref('board.open_board_my_dash_action')
        record_id1 = self.env.ref('dashboard_custom.sale_dashboard_title_action')
        menu = self.env.ref('base.menu_board_root').id 
        list_temp={}
        list_temp['record_id']=record_id.id
        list_temp['menu']=int(menu)
        return list_temp

    @api.multi
    def Check_records(self,action_id):
        action = self.env['ir.actions.act_window'].sudo().search([('id','=',action_id['action_id'])])
        action_data={'action':action.id,
                    'object_name':action.res_model,
                    'name':action.name}
        return action_data


    @api.multi
    def count_records(self,kwargs):
        if kwargs.get('domain'):
            domain_list = ast.literal_eval(kwargs['domain'])
        else:
            domain_list=kwargs['domain']
        action = self.env['ir.actions.act_window'].sudo().search([('id','=',kwargs['action_id'])])
        Model = self.env[action.res_model]
        if domain_list:
            length_records=len(Model.sudo().search(domain_list))
        else:
            length_records=len(Model.sudo().search([]))
        
        records={'action_id':kwargs['action_id'],'length_records':length_records,'serial_no':int(kwargs['serial_no'])}
        return records



class DashboardTile(models.Model):

    _name = 'dashboard.tile'
    


    AVAILABLE_PRIORITIES = [
        ('0', 'Low'),
        ('1', 'High')
        ]



    name   =  fields.Char('Name', required=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Priority', index=True, default='0')
    dashboad_id = fields.Many2one('ir.model',string="Dashboard")
    menuitem_id = fields.Many2one('ir.ui.menu',string="Menu Item")
    view_type   = fields.Char(string="Format")
    action_id = fields.Many2one('ir.actions.actions', string="Action")
    xml_id = fields.Char('External ID')
    model_id = fields.Selection(selection='_list_all_models', compute='get_dashboard_model_id', string='Model', required=True)


    state = fields.Selection(
        [('draft', 'Draft'),('active', 'ACTIVE'),
         ('inactive', 'INACTIVE')], default='draft', string='Stage')

    dash_count = fields.Integer('Count',compute='record_count')
    team_ids = fields.One2many(
        'crm.team','dashboard_tile_id',
        string='Team',
        )

    user_ids = fields.One2many(
        'res.users','dashboard_tile_id',
        string='Users',
        )

    image    = fields.Binary("Image")



    @api.multi
    @api.depends('dashboad_id')
    def get_dashboard_model_id(self):
        for rec in self:
            self.model_id = rec.dashboad_id.model
            



    @api.model
    def _list_all_models(self):
        self._cr.execute("SELECT model, name FROM ir_model ORDER BY name")
        return self._cr.fetchall()

    @api.model
    def get_details_wizard(self, action_id,context_to_save,domain,view_mode,name,menu_name,modal_name,menuitem_id,xml_id):
        model_id = self.env['ir.model'].search([('model','=',modal_name)])
        domain=ast.literal_eval(str(domain))
        list_domain = [list(element) for element in domain]
        domain_list=[]
        for dom in domain:
            domain_list.append(tuple(dom))
        dashboard_new = self.env['dashboard.tile']
        dashboard_id = dashboard_new.create({
            'name': name,
            'dashboad_id':model_id.id,
            'menuitem_id':menuitem_id,
            'dash_search': str(domain_list),
            'view_type': view_mode,
            'action_id': action_id,
            'xml_id': xml_id,
            # 'image': self.image
            })
        filter_obj = self.env['ir.filters'].search([('dashboard_id', '=', dashboard_id.id)])
        if not filter_obj:
            context = {}
            if context_to_save.get('group_by'):
                context = {'group_by': context_to_save['group_by']} 
            filter_vals = {'name': name, 'user_id': False, 'model_id': model_id.model, 'is_default': True, 'active': True, 'action_id': action_id, 'domain': list_domain, 'dashboard_id': dashboard_id.id, 'for_dashboard': True, 'context': context}
            filter_obj = self.env['ir.filters'].create(filter_vals)
        return True

    @api.multi
    def get_dashboard_action(self):
        filter_obj = self.env['ir.filters'].search([('dashboard_id', '=', self.id)])
        action = self.env.ref(self.xml_id).read()[0]
        context = ast.literal_eval(action['context'])
        context.update(dashboard=1, filter=filter_obj.id)
        action.update(context=str(context), view_mode=self.view_type, views=[(False, self.view_type), (False, 'form')])
        return action
        
    @api.multi
    def record_count(self):
        context = ''
        for rec in self:
            if rec.dash_search != False:
                domain=ast.literal_eval(rec.dash_search)
                domain_list=[]
                for dom in domain:
                    domain_list.append(tuple(dom))
                rec.dash_count= len(self.env[rec.dashboad_id.model].search(domain_list).ids)
            else:
                rec.dash_search=0

    dash_search = fields.Text('Search')



class Team(models.Model):
        
    _inherit = 'crm.team'

    name   =  fields.Char('Name')
    visible = fields.Boolean("Visible")
    display   = fields.Selection([
        ('team documents', 'Team Documents'),
        ('user documents', 'User Documents'),
        ('all documents', 'All Documents'),
        
        ],string="Display")
    dashboard_tile_id = fields.Many2one('dashboard.tile',string="Dashboard")


class Users(models.Model):
        
    _inherit = 'res.users'


    name   =  fields.Char('Name')
    visible = fields.Boolean("Visible")
    display   = fields.Selection([
        ('team documents', 'Team Documents'),
        ('user documents', 'User Documents'),
        ('all documents', 'All Documents'),
        
        ],string="Display")
    dashboard_tile_id = fields.Many2one('dashboard.tile',string="Dashboard")



class IrActionsActWindow(models.Model):
    _inherit = 'ir.actions.act_window'

    icon_type     = fields.Selection([ ('image', 'Image'),('class_icon', 'Class Icom'),],default="image",string="Select icon")
    class_name    = fields.Char("Class name")
    image    = fields.Binary("Image")

class IrFilters(models.Model):
    _inherit = 'ir.filters'

    dashboard_id = fields.Many2one('dashboard.tile', 'Dashboard')
    for_dashboard = fields.Boolean('For Dashboard')
