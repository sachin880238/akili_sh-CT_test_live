from odoo import api, fields, models, _  

class DynamicListView(models.Model):
    _name = 'ak.backend.listview'

    name = fields.Char(string="Name")
    user_id = fields.Many2one('res.users', string="User ID")
    object_id = fields.Many2one('ir.model', string="Object ID")
    field_ids = fields.One2many('ak.dynamic.field', 'backend_listview_id', string="Field Ids")
    action_id = fields.Many2one("ir.actions.actions",string="Action")
    @api.model
    def custom_get_status_field(self,action_id,model_name):
        if action_id != None:
            current_user = self.env.user
            back_listview_obj = self.env['ak.backend.listview']
            object_id = self.env['ir.model'].search([('model','=',model_name)])
            action_id = self.env['ir.actions.actions'].sudo().search([('id','=',int(action_id))])
            field_list=[]
            fields_record=self.env['ak.backend.listview'].search([('user_id','=',current_user.id),('object_id','=',object_id.id),('action_id','=',action_id.id)])
            if fields_record:
                for rec in fields_record.field_ids:
                    field_list.append([rec.field_id.name,rec.invisible_status])
                return field_list
            else:
                return True
        else:
            return True




        
    @api.model
    def custom_get_view_id(self,field_data=[]):
        for field in field_data:
            current_user = self.env.user
            back_listview_obj = self.env['ak.backend.listview']
            object_id = self.env['ir.model'].search([('model','=',field[0])])
            field_id =self.env['ir.model.fields'].search([('name','=',field[2]),('model_id','=',object_id.id)])
            if field[3] != None:
                action_id = self.env['ir.actions.actions'].sudo().search([('id','=',int(field[3]))])
                fields_record=self.env['ak.backend.listview'].search([('user_id','=',current_user.id),('object_id','=',object_id.id),('action_id','=',action_id.id)])
                if fields_record:
                    check_count=0
                    status_record=0
                    for field_record in fields_record:
                        for rec in field_record.field_ids:
                            if rec.field_id.id == field_id.id and rec.invisible_status != field[1]:
                                status_record=1
                                rec.write({'invisible_status':field[1]})
                            elif rec.field_id.id == field_id.id and rec.invisible_status == field[1]:
                                check_count=1
                                check_count=check_count+1

                        if check_count ==0 and status_record == 0:
                            field_record.write({'field_ids':[(0,0,{'field_id':field_id.id,'invisible_status':field[1]})]})
                else:
                    field_vals={
                            'name':current_user.name,
                            'user_id':current_user.id,
                            'object_id':object_id.id,
                            'action_id':action_id.id,
                            'field_ids':[(0,0,{'field_id':field_id.id,'invisible_status':field[1]})]
                    }
                    back_listview_obj.create(field_vals)



