from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Route(models.Model):
    _inherit = 'stock.location.route'

    @api.multi
    def active_stock_location_rules(self):
        if self.stage == 'draft' or 'inactive':
            self.write({'stage': 'active'})

    @api.multi
    def inactive_stock_location_rules(self):
        if self.stage == 'active':
            self.write({'stage': 'inactive'})

    route_type_id = fields.Many2one("route.type", string="Type", required=True)
    code = fields.Char("Code", related='route_type_id.code')
    stage = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string='Stage', default='draft')
    applications = fields.Selection([('sale', 'Sales'),
                                     ('purchase', 'Purchasing'),
                                     ('manufacturing', 'Manufacturing'),
                                     ('inventory', 'Inventory')], string='Application')
    identifier = fields.Char('Identifier')

    @api.onchange('identifier', 'route_type_id')
    def onchange_identifier(self):
        if self.identifier and self.route_type_id:
            self.name = self.route_type_id.name + '[' + self.identifier + ']'
        elif self.route_type_id:
            self.name = self.route_type_id.name
        elif self.identifier:
            self.name = '[' + self.identifier + ']'
        else:
            self.name = ''

    @api.onchange('route_type_id')
    def onchange_type(self):
        rule_list = []
        self.update({'rule_ids': False})
        for rec in self.route_type_id.rule_lines_ids:
            if not rec.origin or not rec.action or not rec.destination:
                raise UserError(_("Error!, Route rule's Action or Origin or Destination is missing."))
            vals = {
                'picking_type_id': rec.picking_type_id.id,
                'description': dict(rec._fields['action'].selection).get(rec.action) + ' ' + dict(rec._fields['origin'].selection).get(rec.origin) + ' to ' + dict(rec._fields['destination'].selection).get(rec.destination),
                'action': rec.action,
                'auto': rec.auto,
                'name': rec.name,
                'code': rec.name,
                'procure_method': rec.procure_method,
            }
            rule_list.append((0, 0, vals))
        self.update({'rule_ids': rule_list})

    def activate_route(self):
        self.stage = 'active'

    def inactivate_route(self):
        self.stage = 'inactive'

    def reset_route(self):
        self.stage = 'draft'
