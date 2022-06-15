from odoo import fields, models, _

class Location(models.Model):
    _inherit = "stock.location"
    
    new_move_id = fields.Many2one('stock.move', "Move")
    is_open = fields.Boolean("Is a Open Location ?")

    def name_get(self):
        ret_list = []
        for location in self:
            if location._context.get('product_id') and not location._context.get('bin_size'):
                total = 0.0
                uom = ''
                orig_location = location
                name = location.name
                while location.location_id and location.usage != 'view':
                    location = location.location_id
                    if not name:
                        raise UserError(_('You have to set a name for this location.'))
                    name = location.name + "/" + name
                for qt in orig_location.quant_ids:
                    if qt.product_id.id == orig_location._context['product_id']:
                        total += (qt.quantity - qt.reserved_quantity)
                        uom = qt.product_uom_id.name
                total = int(total)
                uom = str(uom)
                ret_list.append((orig_location.id, "{} ({}) {}".format(name, total, uom)))
            else:
                orig_location = location
                name = location.name
                while location.location_id and location.usage != 'view':
                    location = location.location_id
                    if not name:
                        raise UserError(_('You have to set a name for this location.'))
                    name = location.name + "/" + name
                ret_list.append((orig_location.id, name))
        return ret_list
