from odoo import api, fields, models, _  

class DynamicField(models.Model):
    _name = 'ak.dynamic.field'

    field_id = fields.Many2one('ir.model.fields', string="Field ID")
    backend_listview_id = fields.Many2one('ak.backend.listview', string="Field ID")
    invisible_status = fields.Boolean(string="Invisible Status")
    listview_id = fields.Many2one('ak.backend.listview', string="Field ID")
    object_id = fields.Many2one(related="listview_id.object_id",store=True, string="Object ID")



    # @api.onchange('field_id')
    # def onchange_field_id(self):
    #     print("------------------------",self.backend_listview_id)



    # @api.model
    # def add_field(self):
    #   print("------------------")