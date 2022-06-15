# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import date,datetime


class TransferOrder(models.Model):
    _name = "transfer.order"
    _description = "Transfer Order"
    _inherit = ['mail.thread', 'utm.mixin','mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string="Name", compute='get_full_name')
    partner_id = fields.Many2one('res.partner',string='Account', required=True)
    state = fields.Selection([('draft', 'DRAFT'),('wait', 'WAIT'),('review','REVIEW'),('pick', 'PICK'),('pack', 'PACK'),('assign', 'ASSIGN'),('done', 'DONE'),('cancel','CANCEL'),],
                             string='Status', default='draft')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    source_location_id = fields.Many2one('stock.location',string='Origin Location')
    source_address = fields.Text(string='Origin Address',compute='get_complete_origin_address')
    dest_location_id = fields.Many2one('stock.location',string='Destination Location')
    dest_location_address = fields.Text(string='Destination Address',compute='get_complete_dest_address')
    document = fields.Char(string='Document',index=True, copy=False, default='New')
    ref = fields.Char(string='Reference')
    create_date = fields.Datetime(string='Date')
    priority = fields.Selection([(' ', 'Very Low'), ('x', 'Low'), ('x x', 'Normal'), ('x x x', 'High')], string='Priority',index="True")
    sequence = fields.Char(string='Order Reference')
    team_id = fields.Many2one('crm.team', string='Team')
    assigned = fields.Many2one('res.users', string='Assigned')
    route_id = fields.Many2one('stock.location.route', string='Route')
    carrier_id = fields.Many2one('delivery.carrier', string='Via')
    due_date  = fields.Datetime(string='Due Date')
    transfer_order_line_ids = fields.One2many('transfer.order.lines','transfer_id')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_transfer_order_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_transfer_order_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
    is_copy = fields.Boolean(string='Is Copy', default=False)

    def copy(self, default=None):
        if not self.is_copy:
            self.is_copy = True
        return super(TransferOrder, self).copy(default=default)

    @api.multi
    def get_full_name(self):
        string = 'TO'
        for rec in self:
            if rec.partner_id and rec.document:
                rec.name = '[' + rec.document.replace(string,'') + ']' + ' ' +rec.partner_id.name 
            else:
                rec.name = rec.partner_id.name
            if rec.is_copy:
                rec.name = _("%s (Copy)") % rec.name
                rec.is_copy = False

    @api.multi
    def action_wait(self):
        return True

    @api.multi
    def action_confirm_transfer(self):
        count = 0
        stock_picking_env = self.env['stock.picking']
        for rec in self.transfer_order_line_ids:
            if rec.route_id.rule_ids[0].location_src_id == self.source_location_id and\
               rec.route_id.rule_ids[-1].location_id == self.dest_location_id:
                for line in rec.route_id.rule_ids:
                    values = {}
                    vals = {}
                    products = [] #Collecting move lines
                    vals = {'product_id'      :rec.product_id.id,
                            'name'            :rec.product_id.name,
                            'product_uom'     :rec.uom_id.id,
                            'product_uom_qty' :rec.req_qty,
                            'location_id'     :line.location_src_id.id,
                            'location_dest_id':line.location_id.id,
                            'transfer_id':rec.transfer_id,
                            }
                    products.append((0,0,vals))
                    values = {
                            'partner_id' : self.partner_id.id,
                            'parent_id' : self.partner_id.id,
                            'picking_type_id' : line.picking_type_id.id,
                            'location_id' : line.location_src_id.id,
                            'location_dest_id' : line.location_id.id,
                            'origin' : self.document,
                            'reference' : self.ref,
                            'carrier_id': self.carrier_id.id,
                            'priority1': self.priority,
                            'team_id': self.team_id.id,
                            'assigned': self.assigned.id,
                            'move_ids_without_package' : products
                            }
                    picking = stock_picking_env.create(values)
                    if count == 0:
                        picking.write({'state':'assigned'})
                    else:
                        picking.write({'state':'waiting'})
                    count += 1

    @api.model
    def create(self, vals):
        vals['document'] = self.env['ir.sequence'].next_by_code('transfer.order')
        return super(TransferOrder, self).create(vals)

    @api.multi
    @api.depends('source_location_id.partner_id')
    def get_complete_origin_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])    
        if self.source_location_id.partner_id:
            for rec in self.source_location_id.partner_id:
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
            self.source_address = str(complete_address)
        else:
            self.origin_addr = False

    @api.multi
    @api.depends('dest_location_id.partner_id')
    def get_complete_dest_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])    
        if self.dest_location_id.partner_id:
            for rec in self.dest_location_id.partner_id:
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
            self.dest_location_address = str(complete_address)
        else:
            self.dest_location_address = False
