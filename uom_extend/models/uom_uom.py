from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError, ValidationError
from odoo import modules
import base64

def get_default_img():
    with open(modules.get_module_resource('uom_extend', 'static/img', 'camera.png'),
              'rb') as f:
        return base64.b64encode(f.read())

class UoMCategory(models.Model):
    _inherit = 'uom.category'
    
    measure_type = fields.Selection([
        ('count', 'Counts'),
        ('weight', 'Weight'),
        ('length', 'Length'),
        ('volume', 'Volume'),
        ('time', 'Time'),
    ], string="Type of Measure")

    _sql_constraints = [
        ('uom_category_unique_type', 'UNIQUE(measure_type)', 'You can have only one category per measurement type.'),
    ]

class UoM(models.Model):
    _inherit = 'uom.uom'
    _order = 'sequence,id'

    image = fields.Binary(attachment=True, default=get_default_img())
    unit_qty = fields.Float('Unit Quantity', default=1.0, digits=0, required=True)
    reference = fields.Many2one('uom.uom', 'Reference Unit')
    reference_qty = fields.Float('Reference Quantity', default=1.0, digits=0, required=True)
    state = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string='Stage', required=True, readonly=True, copy=False, default='active')
    sequence = fields.Integer(required=True, default=1)
    unit_name = fields.Char(compute="get_unit_name")
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_uom_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_uom_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    def set_to_draft(self):
        self.state = 'draft'
        self.active = False

    def set_to_active(self):
        self.state = 'active'
        self.active = True

    def set_to_inactive(self):
        self.state = 'inactive'
        self.active = False

    @api.depends('name')
    def get_unit_name(self):
        self.unit_name = self.name
