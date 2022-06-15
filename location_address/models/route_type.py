from odoo import models, fields, api


class RouteType(models.Model):
    _name = 'route.type'

    sequence = fields.Integer(string='sequence')
    name = fields.Char('Name', compute='_get_route_type_name')
    code = fields.Char('Code', required=True)
    description = fields.Char('Description')
    application = fields.Selection([('sale', 'Sales'),
                                    ('purchase', 'Purchasing'),
                                    ('manufacturing', 'Manufacturing'),
                                    ('inventory', 'Inventory')], string='Application')
    rule_lines_ids = fields.One2many('route.rule.type', 'route_type_id', 'Rules', copy=True)
    stage = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string='Stage', default='draft')

    @api.multi
    def name_get(self):
        result = []
        for route_type in self:
            result.append((route_type.id, "{} ({})".format(route_type.code, route_type.description)))
        return result

    @api.depends('code')
    def _get_route_type_name(self):
        for route_type in self:
            route_type.name = route_type.code

    @api.onchange('rule_lines_ids')
    def _onchange_rule_lines(self):
        self.code = ''
        self.description = ''
        for rule in self.rule_lines_ids:
            if rule.picking_type_id.type_code:
                self.code += rule.picking_type_id.type_code
            if self.rule_lines_ids[-1] == rule:
                self.description += rule.picking_type_id.name
            else:
                self.description += rule.picking_type_id.name + ', '

    def activate_route(self):
        self.stage = 'active'

    def inactivate_route(self):
        self.stage = 'inactive'

    def reset_route(self):
        self.stage = 'draft'
