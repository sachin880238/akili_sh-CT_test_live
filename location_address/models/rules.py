from odoo import models, fields, api


class RouteRuleType(models.Model):
    _name = 'route.rule.type'

    @api.depends('route_type_id', 'picking_type_id')
    def _get_rule_name(self):
        for rule in self:
            if rule.route_type_id:
                rule.name = rule.route_type_id.name + '_' + rule.picking_type_id.name
            else:
                rule.name = rule.picking_type_id.name

    route_type_id = fields.Many2one("route.type", string='Route Type')
    sequence = fields.Integer(string='sequence')
    name = fields.Char('Name', compute='_get_rule_name')
    action = fields.Selection([('pull', 'pull from'), ('push', 'push to'), ('pull_push', 'pull & push'),
                               ('manufacture', 'manufacture'), ('buy', 'buy')], string='Action', required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True)
    active = fields.Boolean('Active', default=True, help="If unchecked, it will allow you to hide the rule without removing it.")
    auto = fields.Selection([('manual', 'Manual Operation'), ('transparent', 'Automatic No Step Added')], string='Automatic Move',
                            default='manual', index=True, required=True,
                            help="The 'Manual Operation' value will create a stock move after the current one. "
                            "With 'Automatic No Step Added', the location is replaced in the original move.")
    procure_method = fields.Selection([('make_to_stock', 'Take From Stock'), ('make_to_order', 'Trigger Another Rule')], string='Supply Method',
                                      default='make_to_stock', help="""Create Procurement: A procurement will be created in the source location and the system will try to find a rule to resolve it. The available stock will be ignored. Take from Stock: The products will be taken from the available stock.""")
    route_id = fields.Many2one('stock.location.route', 'Route', ondelete='cascade')
    route_sequence = fields.Integer('Route Sequence', related='route_id.sequence', store=True, readonly=False, compute_sudo=True)
    stage = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string='Stage', default='draft')
    origin = fields.Selection([('stock', 'stock location'),
                               ('shipping', 'shipping location'),
                               ('customer', 'customer location'),
                               ('vendor', 'vendor location'),
                               ('packing', 'packing location'),
                               ('receiving', 'receiving location'),
                               ('manufacturing', 'manufacturing location'),
                               ('inspect', 'inspection location')], string='Origin')
    destination = fields.Selection([('stock', 'stock location'),
                                    ('shipping', 'shipping location'),
                                    ('customer', 'customer location'),
                                    ('vendor', 'vendor location'),
                                    ('packing', 'packing location'),
                                    ('receiving', 'receiving location'),
                                    ('manufacturing', 'manufacturing location'),
                                    ('inspect', 'inspection location')], string='Destination')
