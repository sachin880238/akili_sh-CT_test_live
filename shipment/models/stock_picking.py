from odoo import api, fields, models, _
from datetime import datetime

PROCUREMENT_PRIORITIES = [
    (' ', ' '),
    ('x', '*'),
    ('x x', '**'),
    ('x x x', '***'),
]

class Picking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'barcodes.barcode_events_mixin']

    def copy(self, default=None):
        if not self.is_copy:
            self.is_copy = True
        return super(Picking, self).copy(default=default)

    @api.returns('self')
    def _default_stage(self):
        return self.env['stock.picking.states'].search([], limit=1)

    status = fields.Many2many("stock.picking.states", default=_default_stage)
    is_copy = fields.Boolean(string='Copy',default=False, help='It will help to find out whether record has been copied or not.')
    partner_shipping_id = fields.Many2one('res.partner','Shipping Address',compute="get_custom_details")
    partner_shipping_address = fields.Text('Shipping Address',compute="get_custom_details")
    scheduled_date = fields.Datetime('Scheduled Date', track_visibility='onchange',
        help="Scheduled.")
    route_id = fields.Many2one("stock.location.route", string="Route")
    partner_id = fields.Many2one('res.partner')
    parent_id = fields.Many2one('res.partner', string='Account',compute="get_custom_details",readonly=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    origin_addr = fields.Text(compute='get_complete_origin_address',)
    dest_addr = fields.Text(compute='get_complete_dest_address',)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country')
    team_id = fields.Many2one('crm.team', string='Team')
    shipper = fields.Many2one('res.users',"Shipper", group_expand='_expand_stages')
    reference = fields.Char("Reference")
    carrier_id = fields.Many2one('delivery.carrier', string="Ship Via")
    priority1 = fields.Selection(PROCUREMENT_PRIORITIES, 'Priority')
    is_shipment = fields.Boolean('Is Shipment')
    date_due = fields.Datetime(string='Due Date')
    packer = fields.Many2one('res.users',"Packer")
    required = fields.Char("Required")
    stock_documents_ids = fields.One2many('stock.documents',"picking_id")
    barcode = fields.Char(string='Barcode',store=False)
    shipment = fields.Char(string='Shipment')
    assigned = fields.Many2one('res.users',"Assigned")
    present = fields.Char(string="Time left",compute="get_extimate_shipping_time")
    cart_name = fields.Char(compute='get_cart_name')
    stock_content_ids = fields.One2many('stock.content', 'picking_id')
    stock_container_ids = fields.One2many('stock.container', 'picking_id')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    picking_status = fields.Char(compute="get_picking_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_picking_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.picking_status = "#006400"
            elif rec.parent_state == "yellow":
                rec.picking_status = "#FFD700"
            elif rec.parent_state == "red":
                rec.picking_status = "#FF0000"
            else:
                rec.picking_status = "#000000"

    @api.multi
    @api.depends('location_id.partner_id')
    def get_complete_origin_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])    
        if self.location_id.partner_id:
            for rec in self.location_id.partner_id:
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
            self.origin_addr = str(complete_address)
        else:
            self.origin_addr = False
    @api.multi
    @api.depends('location_dest_id.partner_id')
    def get_complete_dest_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])    
        if self.location_dest_id.partner_id:
            for rec in self.location_dest_id.partner_id:
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
            self.dest_addr = str(complete_address)
        else:
            self.dest_addr = False

    @api.onchange('is_shipment')
    def get_picking_type(self):
        if self.is_shipment:
            picking_type = self.env['stock.picking.type'].search([('name','=','Delivery Orders')])
            src_location = self.env['stock.location'].search([('name','=','Stock')])
            self.picking_type_id = picking_type
            self.location_id = src_location 
        return {}

    @api.depends('partner_id')
    def get_custom_details(self):
        for rec in self:
            if rec.partner_id:
                partner = rec.partner_id
                rec.parent_id = partner.parent_id
                rec.partner_shipping_id = partner
                b = c = d = ' '
                if partner.street:
                    b += partner.street
                if partner.street2 :
                    c += partner.street2
                if partner.city and partner.state_id and partner.zip :
                    d += partner.city + " " + partner.state_id.code + " " + partner.zip
                elif partner.city and partner.state_id and not partner.zip:
                    d += partner.city + " " + partner.state_id.code
                elif partner.city and partner.zip and not partner.state_id:
                    d += partner.city + " " + partner.zip
                elif partner.state and partner.zip and not partner.city :
                    d += partner.state_id.code + " " + partner.zip

                if partner.city and not partner.state_id and not partner.zip:
                    d += partner.city

                if partner.state_id and not partner.city and not partner.zip:
                    d += partner.state_id.code

                if partner.zip and not partner.city and not partner.state_id:
                    d += partner.zip
                temp_shipping = str(b+"\n"+c+"\n"+d)
                rec.partner_shipping_address = temp_shipping

    @api.depends('date_due')
    def get_extimate_shipping_time(self):
        for record in self:
            if record.date_due:
                diff = record.date_due - datetime.now()
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                record.present = str(hours) + ':' + str(minutes)

    cart_name = fields.Char(compute='get_cart_name')

    def get_cart_name(self):
        if self.name:
            if self.partner_id.name:
                self.cart_name = self.name + ' ' + self.partner_id.name
            elif self.partner_id.comp_name:
                self.cart_name = self.name + ' ' + self.partner_id.comp_name
            else:
                self.cart_name = self.name
        if self.is_copy:
            if self.cart_name:
                self.cart_name = _("%s (Copy)") % self.cart_name
                self.is_copy = False

    def on_barcode_scanned(self, barcode):
        return {}

    @api.model 
    def on_barcode_scanned1(self, url_dict={}):

        move_obj = self.env['stock.move']
        view_id=self.env.ref('stock.view_move_picking_form').id
        picking_id = self.env['stock.picking'].search([('id','=',int(url_dict['picking_id']))])
        
        if url_dict['tag'] == 'PRODUCTS':    
            product_id = self.env['product.product'].search([('barcode','=',url_dict['barcode'])])
            
            if not product_id:
                return {'warning': {
                            'title': _('Product not found'),
                            'message': _('Product Not Found')
                        }}
            # line = move_obj.search([('product_id','=',product_id.id)])
            for line1 in picking_id.move_ids_without_package:

                if line1.product_id.id==product_id.id:
                    return {
                            'res_id': [ line1.id, ],
                            'view_id':view_id,
                            'picking_id':line1.picking_id.id,
                            }
                else :
                    return {}                      
        
    def action_split(self):
        pass    

    def _expand_stages(self, states, domain, order):
        stage_ids = self.env['res.users'].search([('warehouse_team','=',True)])
        return stage_ids

class PickingType(models.Model):
    _inherit = "stock.picking.type"

    def _get_only_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        return action

    def get_action_picking_form(self):
        if self.name == "Delivery Orders":
            return self._get_only_action('shipment.custom_action_picking_form')
        else:
            return self._get_only_action('stock.action_picking_form')

    def get_action_picking_tree_late(self):
        if self.name == "Delivery Orders":
            return self._get_action('shipment.custom_picking_tree_late')
        else:
            return self._get_action('stock.action_picking_tree_late')

    def get_action_picking_tree_backorder(self):
        if self.name == "Delivery Orders":
            return self._get_action('shipment.custom_picking_tree_backorder')
        else:
            return self._get_action('stock.action_picking_tree_backorder')

    def get_action_picking_tree_waiting(self):
        if self.name == "Delivery Orders":
            return self._get_action('shipment.custom_picking_tree_waiting')
        else:
            return self._get_action('stock.action_picking_tree_waiting')

    def get_only_action_picking_tree_ready(self):
        if self.name == "Delivery Orders":
            return self._get_only_action('shipment.custom_picking_tree_ready')
        else:
            return self._get_only_action('stock.action_picking_tree_ready')

    def get_action_picking_tree_ready(self):
        if self.name == "Delivery Orders":
            return self._get_action('shipment.custom_picking_tree_ready')
        else:
            return self._get_action('stock.action_picking_tree_ready')

    def get_stock_picking_action_picking_type(self):
        if self.name == "Delivery Orders":
            return self._get_action('shipment.delivery_order_action')
        else:
            return self._get_action('stock.stock_picking_action_picking_type')

class StockPickingStates(models.Model):
    _name = "stock.picking.states"
    _description = "Shipment States"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char(string='Name')
    sequence = fields.Integer(string='Sequence')
