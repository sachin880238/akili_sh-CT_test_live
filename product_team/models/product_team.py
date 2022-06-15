# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _ 
from odoo.exceptions import UserError


class Team(models.Model):
    _inherit = 'crm.team'
    _description = 'Sales Channels'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    name = fields.Char()
    pro_manager = fields.Many2one('res.users', string='Product Manager')
    user_ids = fields.Many2many('res.users', string='List of Users',)
    sales_team = fields.Boolean("Sales Team")
    purchase_team = fields.Boolean("Purchasing Team")
    warehouse_team = fields.Boolean("Warehouse Team")
    desc = fields.Text(string="Description")
    state = fields.Selection([('active', 'ACTIVE'),('inactive', 'INACTIVE')], default='active', track_visibility='onchange', readonly=True, copy=False)

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_teams_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_teams_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    @api.depends('state')
    def get_team_state(self):
        if self.state == 'active':
            self.state = 'inactive'
        elif self.state  == 'inactive':
            self.state = 'active'

class Product(models.Model):
    _inherit = "product.category"

    review_category_id = fields.Many2one(
        'crm.team',
        'Sales Review Category', domain=[('sales_team', '=', True)]
    )

    purchase_review_category_id = fields.Many2one(
        'crm.team',
        'Purchase Review Category', domain=[('purchase_team', '=', True)]
    )

    team_ids = fields.Many2many('crm.team', string='Teams')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_team_id = fields.Many2one('crm.team',string='Product Group',)
