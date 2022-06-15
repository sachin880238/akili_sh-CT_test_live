from odoo import fields, models, _, api

class StockContainerType(models.Model):
    _name = "stock.container.type"
    _description = "Container Types"
    
    _order = 'sequence'
    sequence = fields.Integer(string="Sequence")
    name = fields.Char('Name', required=True)
    image = fields.Binary(string="Image")
    dim1 = fields.Float('Dime 1')
    dim2 = fields.Float('Dime 2')
    dim3 = fields.Float('Dime 3')
    surcharge = fields.Float('Surcharge')
    weight = fields.Float('Weight')
    comment = fields.Char('Comments')
    icon   = fields.Many2one('stock.container.type.icon',string="Icon")
    state  = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'),('inactive','INACTIVE')], required=True, index=True, default='draft')

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_container_type_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_container_type_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"


class StockContainerTypeIcon(models.Model):
    _name = "stock.container.type.icon"
    _description = "Container Types Icons"

    name = fields.Char('Name', required=True)
    image = fields.Binary(string="Image")
