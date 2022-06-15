from odoo import models, fields, api


class Locations(models.Model):
    _inherit = 'stock.location'

    def get_location_complete_name(self):
        for line in self:
            code = ''
            if line.barcode:
                code = '[' + line.barcode + ']'
                if line.display_code:
                    code = code + ' ' + line.display_code
                if line.code:
                    code = code + ' ' + '/' + line.code
            elif line.display_code and line.code:
                code = line.display_code+'/'+line.code
            else:
                code = line.name
            line.full_name = code
        return True

    @api.multi
    def active_location(self):
        if self.stage == 'draft' or 'inactive':
            self.write({'stage': 'active'})

    @api.multi
    def inactive_location(self):
        if self.stage == 'active':
            self.write({'stage': 'inactive'})

    sequence = fields.Integer(string='sequence')
    stock_count = fields.Integer(string='Stock')
    rules_count = fields.Integer(string='Rules')
    is_ct_shipping_location = fields.Boolean(string='Shipping')
    is_ct_receiving_location = fields.Boolean(string='Receiving')
    is_ct_manufacturing_location = fields.Boolean(string='Manufacturing')
    is_ct_assembly_location = fields.Boolean(string='Assembly')
    is_ct_inspection_location = fields.Boolean(string='Inspection')
    is_ct_staging_location = fields.Boolean(string='Staging')
    is_ct_packing_location = fields.Boolean(string='Packing')
    code = fields.Char('Code')
    display_code = fields.Char(string='Code', compute='set_code', store=True)
    stage = fields.Selection([('draft', 'DRAFT'),
                              ('active', 'ACTIVE'),
                              ('inactive', 'INACTIVE')], string='Stage', default='draft')
    address = fields.Char('Address')
    partner_id = fields.Many2one('res.partner', string='Address')
    partner_addr1 = fields.Text(compute='get_complete_invoice_address',)
    sequence = fields.Integer(string='sequence',)
    full_name = fields.Char(compute=get_location_complete_name, string="Full Name")
    inventory_function = fields.Selection([('stock', 'Stock'), ('scrap', 'Scrap'),('transit', 'Transit'),
                                           ('loss', 'Loss')], string='Inventory' )
    
    
    @api.one
    @api.depends('code', 'location_id.display_code')
    def set_code(self):
        if self.location_id.display_code:
            self.display_code = self.location_id.display_code
        else:
            self.display_code = self.code

    @api.onchange('partner_id')
    def get_children_loc_from_child_loc(self):
        location_env = self.env['stock.location']
        for rec in self:
            if rec.location_id:
                children_ids = location_env.search([('location_id','=',rec._context['params']['id'])])
                for location in children_ids:
                    location.write({'partner_id' : rec.partner_id.id})

    @api.multi
    @api.depends('partner_id')
    def get_complete_invoice_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])    
        if self.partner_id:
            for rec in self.partner_id:
                complete_address = ''
                if rec.name:
                    complete_address += rec.name
                    if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.comp_name: 
                    complete_address += rec.comp_name
                    if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street: 
                    complete_address += rec.street
                    if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street2: 
                    complete_address += rec.street2
                    if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and not rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.zip and not rec.state_id : 
                    complete_address += rec.city + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and rec.zip and not rec.city : 
                    complete_address += rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and not rec.state_id and not rec.zip: 
                    complete_address += rec.city
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and not rec.city and not rec.zip: 
                    complete_address += rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.zip and not rec.city and not rec.state_id: 
                    complete_address += rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if self.company_id:
                    if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                        complete_address += ''
                    else:
                        complete_address += rec.country_id.name if rec.country_id else '' if rec.country_id else ''
            self.partner_addr1 = str(complete_address)
        else:
            self.partner_addr1 = False
