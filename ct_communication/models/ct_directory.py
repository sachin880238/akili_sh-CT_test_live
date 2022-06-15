from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Accounts'

    dir_type = fields.Char(string="Type", compute="get_address_type")

    @api.multi
    def get_address_type(self):
        for rec in self:
            if not rec.parent_id and rec.supplier == True:
                rec.dir_type = 'Vendor Account'
            elif rec.parent_id and rec.parent_id.supplier == True:
                if rec.vendor_addr_type == 'purchase':
                    rec.dir_type = 'Vendor ' + 'Purchasing'
                if rec.vendor_addr_type == 'contact':
                    rec.dir_type = 'Vendor ' + 'Contact'
                if rec.vendor_addr_type == 'invoice':
                    rec.dir_type = 'Vendor ' + 'Payment'
                if rec.vendor_addr_type == 'delivery':
                    rec.dir_type = 'Vendor ' + 'Shipping'

            if not rec.parent_id and rec.customer == True:
                rec.dir_type = 'Customer Account'
            elif rec.parent_id and rec.parent_id.customer == True:
                if rec.type_extend == 'contact':
                    rec.dir_type = 'Customer ' + 'Contact'
                if rec.type_extend == 'invoice':
                    rec.dir_type = 'Customer ' + 'Billing'
                if rec.type_extend == 'delivery':
                    rec.dir_type = 'Customer ' + 'Shipping'

    @api.model
    def create(self,vals):
        res = super(ResPartner, self).create(vals)
        directory = self.env['ct.directory']
        for rec in res:
            if rec.email:
                values={}
                values['descriptor'] = 'Email'
                values['identifier'] = rec.email
                values['partner_id']=rec.id
                directory.create(values)
            if rec.phone:
                values={}
                values['descriptor'] = rec.primary_tel_type.name
                values['identifier'] = rec.phone
                values['partner_id'] = rec.id
                directory.create(values)
            if rec.alternate_communication_1:
                values={}
                values['descriptor'] = rec.alternate_commu_type_1.name
                values['identifier'] = rec.alternate_communication_1
                values['partner_id'] = rec.id
                directory.create(values)
            if rec.alternate_communication_2:
                values={}
                values['descriptor'] = rec.alternate_commu_type_2.name
                values['identifier'] = rec.alternate_communication_2
                values['partner_id'] = rec.id
                directory.create(values)
        return res

    @api.one
    def write(self,vals):
        if 'email' in vals:
            directory = self.env['ct.directory'].search([('partner_id', '=', self.id),('descriptor','=','email')])
            if directory:
                values = {'identifier': vals['email']}
                directory.write(values)
            else:
                values = {'descriptor': 'email', 'identifier': vals['email'], 'partner_id': self.id}
                directory.create(values)
        
        if 'phone' in vals:
            directory = self.env['ct.directory'].search([('partner_id', '=', self.id),('descriptor','=',self.primary_tel_type.name)])
            if directory:
                values={'identifier': vals['phone']}
                directory.write(values)
            else:
                values = {'descriptor': self.primary_tel_type.name, 'identifier': vals['phone'], 'partner_id': self.id}
                directory.create(values)

        if 'primary_tel_type' in vals:
            directory = self.env['ct.directory'].search([('partner_id', '=', self.id),('identifier','=',self.phone)])
            if directory:
                descriptor = self.env['communication.type'].search([('id','=',vals['primary_tel_type'])])
                values={'descriptor': descriptor.name}
                directory.write(values)
            else:
                descriptor = self.env['communication.type'].search([('id','=',vals['primary_tel_type'])])
                values = {'descriptor': descriptor.name, 'identifier': self.phone, 'partner_id': self.id}
                directory.create(values)

        if 'alternate_communication_1' in vals:
            directory = self.env['ct.directory'].search([('partner_id', '=', self.id),('descriptor','=',self.alternate_commu_type_1.name)])
            if directory:
                values={'identifier': vals['alternate_communication_1']}
                directory.write(values)
            else:
                values = {'descriptor': self.alternate_commu_type_1,  'identifier': vals['alternate_communication_1'], 'partner_id': self.id}
                directory.create(values)

        if 'alternate_commu_type_1' in vals:
            directory = self.env['ct.directory'].search([('partner_id', '=', self.id),('identifier','=',self.alternate_communication_1)])
            if directory:
                descriptor = self.env['communication.type'].search([('id','=',vals['alternate_commu_type_1'])])
                values={'descriptor': descriptor.name}
                directory.write(values)
            else:
                descriptor = self.env['communication.type'].search([('id','=',vals['alternate_commu_type_1'])])
                values = {'descriptor': descriptor.name, 'identifier': self.alternate_communication_1, 'partner_id': self.id}
                directory.create(values)

        if 'alternate_communication_2' in vals:
            directory = self.env['ct.directory'].search([('partner_id', '=', self.id),('descriptor','=',self.alternate_commu_type_2.name)])
            if directory:
                values={'identifier': vals['alternate_communication_2']}
                directory.write(values)
            else:
                values = {'descriptor': self.alternate_commu_type_2,  'identifier': vals['alternate_communication_2'], 'partner_id': self.id}
                directory.create(values)

        if 'alternate_commu_type_2' in vals:
            directory = self.env['ct.directory'].search([('partner_id', '=', self.id),('identifier','=',self.alternate_communication_2)])
            if directory:
                descriptor = self.env['communication.type'].search([('id','=',vals['alternate_commu_type_2'])])
                values={'descriptor': descriptor.name}
                directory.write(values)
            else:
                descriptor = self.env['communication.type'].search([('name','=',vals['alternate_commu_type_2'])])
                values = {'descriptor':descriptor.name, 'identifier': self.alternate_communication_2, 'partner_id': self.id}
                directory.create(values)

        if 'lang' in vals:
            directory = self.env['ct.directory'].search([('partner_id', '=', self.id),('identifier','=','lang')])
            if directory:
                values={'descriptor':vals['lang']}
                directory.write(values)
            else:
                values = {'descriptor':vals['lang'], 'identifier':vals['lang'], 'partner_id': self.id}
                directory.create(values)


        res = super(ResPartner, self).write(vals)
        return res


class CtDirectory(models.Model):
    _name = 'ct.directory'
    _description = 'Conservation Directory'
    
    _rec_name = 'identifier'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    

    directory_type = fields.Char(related="partner_id.dir_type",string="Type")
    partner_id = fields.Many2one('res.partner', string="Account")
    contact_id = fields.Char(related="partner_id.name",string='Contact')
    company_id = fields.Many2one(related="partner_id.company_id", string='Company')
    descriptor = fields.Char(string='Descriptor')
    identifier = fields.Char(string='Identifier')



    def get_address_type(self):
        for rec in self:
            if rec.partner_id.customer:
                rec.directory_type=rec.partner_id.type_extend
            if rec.partner_id.supplier:
                rec.directory_type=rec.partner_id.vendor_addr_type
