from odoo import models, fields, api
from datetime import datetime, timedelta 

class ScheduleActivity(models.Model):

    _inherit = 'calendar.event'

    AVAILABLE_PRIORITIES = [
    (' ', 'Normal'),
    ('x', '1'),
    ('x x', '2'),
    ('x x x', '3'),
    ]

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    activity_type_id = fields.Many2one('mail.activity.type', string="Type")
    activity_link_to = fields.Char(string="Link To")
    activity_link_id = fields.Char(string="Link ID")
    privacy = fields.Boolean(string='Private')
    schedule_link = fields.Integer(string='Link')
    comment = fields.Text(string='Comments')
    task_alarm = fields.Integer(string='Alarm')
    schedule_link = fields.Integer(string='Link')
    start_date = fields.Datetime(string='Start Date')
    start_time = fields.Datetime(string='Start Time')
    due_date = fields.Datetime(string='Due Date')
    due_time = fields.Datetime(string='Due Time')
    time = fields.Integer(string='Minutes')
    is_activity_fixed = fields.Boolean(string="Fixed")
    alarm_ids = fields.Many2one('calendar.alarm', string="Warning")
    activity_priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_event_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_event_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    repeat_task = fields.Selection(selection=[
    	('no','None'),
		('daily', 'Daily'),
		('weekly', 'Weekly'),
		('monthly', 'Monthly'),
		('yearly', 'Yearly'),],
		string='Repeat')

    task_fixed = fields.Selection(selection=[
		('yes','Yes'),
		('no','No')],
		string='Fixed')
    activity_repeat = fields.Selection(selection=[
		('yes','Yes'),
		('no','No')],
		string='Repeat')
    states = fields.Selection(selection=[
    	('draft', 'DRAFT'),
		('schedule', 'SCHEDULED'),
		('done', 'DONE')],
		default='draft')

    def get_schedule_activity_tree_view(self):
        calendar_events = self.search([])
        if len(calendar_events) > 0:
            action = self.env.ref('schedule_activity.action_view_schedule_task').read()[0]
            return action
        else:
	        return {
	                'name': ('Tasks'),
	                'view_type': 'form',
	                'view_mode': 'tree,form',
	                # 'view_id': self.env.ref('schedule_activity.view_schedule_task_tree').id,
	                'res_model': 'calendar.event',
	                # 'domain':[('partner_id','=',self._context.get('active_id', False))],
	                # 'groups_id': [(4, self.env.ref('sales_team.group_sale_salesman').id)],
	                'type': 'ir.actions.act_window',
	                'target': 'current',
	                'context' : {'create':True},
	                }

    @api.multi
    def action_button_confirm(self):
        self.write({'states':'done'}) #Complete schedule activity 
        return True
    # @api.onchange('task_fixed')
    # def fixed_check(self):
    # 	if(self.task_fixed == 'yes'):
    # 		self.task_fixed_t = True
    # 	if(self.task_fixed == 'no'):
    # 		self.task_fixed_t = False

    # @api.onchange('task_repeat')
    # def repeat_check(self):
    # 	if(self.task_repeat == 'yes'):
    # 		self.task_repeat_t = True
    # 	if(self.task_repeat == 'no'):
    # 		self.task_repeat_t = False

    # task_fixed_t = fields.Boolean(string="Fix")
    # task_repeat_t = fields.Boolean(string="Repeat")

    # @api.multi
    # def action_schedule_link(self):
    # 	return True
