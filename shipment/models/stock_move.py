from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.exceptions import UserError

PROCUREMENT_PRIORITIES = [
    (' ', ' '),
    ('x', '*'),
    ('x x', '**'),
    ('x x x', '***'),
]

class StockMove(models.Model):
    _inherit = "stock.move"

    _barcode_scanned = fields.Char("Barcode")
    # location_barcode = fields.Many2one('stock.location',string="Location ID")
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_stock_move_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_stock_move_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
    
    @api.onchange('_barcode_scanned')
    def _on_barcode_scanned(self):
        if self._barcode_scanned:
            barcode = self._barcode_scanned

            container_id = self.env['stock.container'].search([('container_barcode','=',barcode)])
            location_id = self.env['stock.location'].search([('barcode','=',barcode),('is_open','=',False)])
            open_loc_id = self.env['stock.location'].search([('barcode','=',barcode),('is_open','=',True)])

            if location_id:
                self.available_loc = location_id.id

            elif self.available_loc:
                # loc_id = self.env['stock.location'].search([('barcode','=',barcode)])
                # self.available_loc = loc_id.name
                product_id = self.env['product.product'].search([('barcode','=',barcode)])

                if product_id:
                    self.transfer_now += 1


            elif container_id:
                self.container_barcode = container_id.container_barcode
                self.container_type = container_id.container_type
                # self.location_barcode = container_id.location_id

            if open_loc_id:
                self.location_barcode = open_loc_id.barcode

    @api.onchange('container_barcode','location_barcode')
    def get_onchange_container_and_location_values(self):
        for rec in self:
            if rec.container_barcode:
                container = self.env['stock.container'].search([('container_barcode','=',rec.container_barcode)])
                if container:
                    rec.container_type = container.container_type.id
            if rec.location_barcode:
                location = self.env['stock.location'].search([('barcode','=',rec.location_barcode),('usage','=','internal')])
                if location:
                    rec.container_location = location.id
                else:
                    raise UserError(_('Invalid Location ID.'))

    @api.model
    def create(self,vals):
        if self._context.get('params'):
            if self._context['params']['model'] == 'sale.order':
                so_id = self.env['sale.order'].search([('id','=',self._context.get('active_id', False))])
                if so_id.reserve_count > 0:
                    res_loc = self.env['stock.location'].search([('is_loc_reservable','=',True)])
                    vals['location_id'] = res_loc.id
            res = super(StockMove, self).create(vals)
            return res
        elif vals.get('sale_line_id'):
            sol_id = self.env['sale.order.line'].search([('id','=',vals['sale_line_id'])]) 
            so_id = self.env['sale.order'].search([('id','=',sol_id.order_id.id)])
            if so_id.reserve_count > 0:
                res_loc = self.env['stock.location'].search([('is_loc_reservable','=',True)])
                vals['location_id'] = res_loc.id
            res = super(StockMove, self).create(vals)
            return res
        else:
            res = super(StockMove, self).create(vals)
            return res

    @api.depends('product_id')
    def get_stock_available_loc(self):
        picking_id = self.picking_id
        for rec in self:
            if rec.product_id:
                action = self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),('location_id.display_name','ilike',picking_id.location_id.display_name + '%')])
                locations = []
                for qt in action:
                    if qt.location_id.id not in locations:
                       locations.append(qt.location_id.id)
                if locations:
                        rec.location_ids = [(6,0,locations)]


    @api.onchange('available_loc')
    def _on_available_loc(self):
        if self.available_loc:
            self.transfer_now = 0
            for rec in self.available_loc.quant_ids:
                if rec.product_id == self.product_id:
                    quantity = 0
                    self.available_qty = rec.quantity - rec.reserved_quantity
                    break

    #-----Update move lines quantity----

    @api.depends('product_uom_qty')
    def get_wait_product_quantity(self):
        for rec in self:
            if rec.picking_id.status.name == 'ASSIGN':
                ttl = self.available_stock_qty()
                if ttl < rec.product_uom_qty:
                    rec.wait = rec.product_uom_qty - ttl

    @api.depends('product_uom_qty')
    def get_prepare_product_quantity(self):
        blank_list = []
        contianer  = self.env['stock.container']
        for rec in self:
            if rec.picking_id.status.name == 'ASSIGN':
                ttl = self.available_stock_qty()
                if ttl >= rec.product_uom_qty :
                    rec.prepare = rec.product_uom_qty

                elif ttl < rec.product_uom_qty:
                    rec.prepare = ttl

    @api.depends('product_uom_qty')
    def get_release_product_quantity(self):
        for rec in self:
            if rec.picking_id.status.name == 'ASSIGN':
                ttl = self.available_stock_qty()
                if ttl >= rec.product_uom_qty :
                    rec.release = rec.product_uom_qty

                elif ttl < rec.product_uom_qty:
                    rec.release = ttl

    @api.depends('product_uom_qty')
    def get_ship_product_quantity(self):
        for rec in self:
            if rec.picking_id.status.name == 'ASSIGN':
                ttl = self.available_stock_qty()
                if ttl >= rec.product_uom_qty :
                    rec.ship = rec.product_uom_qty

                elif ttl < rec.product_uom_qty:
                    rec.ship = ttl

    @api.depends('product_uom_qty')
    def get_invoice_product_quantity(self):
        for rec in self:
            if rec.picking_id.status.name == 'ASSIGN':
                ttl = self.available_stock_qty()
                if ttl >= rec.product_uom_qty :
                    rec.invoice = rec.product_uom_qty

                elif ttl < rec.product_uom_qty:
                    rec.invoice = ttl
        return

    def _get_product_shiping_instructions(self):
        for rec in self:
            if rec.product_id:
                rec.instructions = rec.product_id.picking_warn_msg or False

    def _set_product_shiping_instructions(self):
        for rec in self:
            if rec.product_id:
                rec.product_id.picking_warn_msg = rec.instructions or False

    wait = fields.Integer("Waiting", readonly=True, compute='get_wait_product_quantity')
    prepare = fields.Integer(string="Process", compute='get_prepare_product_quantity')
    release = fields.Integer(string="Release", compute='get_release_product_quantity')
    ship = fields.Integer(string="Ship", compute='get_ship_product_quantity')
    invoice = fields.Integer("Invoice", compute='get_invoice_product_quantity')
    packer = fields.Many2one('res.users', string="Packer")
    date_due = fields.Date(string='Due Date')
    priority1 = fields.Selection(PROCUREMENT_PRIORITIES, string='Priority')
    carrier_id = fields.Many2one('delivery.carrier', string="Ship Via")
    barcode = fields.Char(string='Barcode')
    location_dest_id = fields.Many2one(
             'stock.location', 'Destination Location',
             auto_join=True, index=True)
    team_id = fields.Many2one('crm.team', string="Team")
    assigned_to = fields.Many2one('res.users', string="Assgined")
    reserved_qty = fields.Integer(string="Reserved")
    location_ids = fields.One2many('stock.location', 'new_move_id', 'Stock Location', compute="get_stock_available_loc")
    available_loc = fields.Many2one('stock.location', string="Location")
    container_barcode = fields.Char(string='Container ID')
    stock_container_id = fields.Many2one('stock.container', string='Container ID')
    container_type = fields.Many2one('stock.container.type', 'Container')
    transfer_now = fields.Integer(string='Transfer Now',default=1)
    serial_no = fields.Many2one('stock.production.lot',string='Serial ID')
    lot_id = fields.Many2one('stock.production.lot', string="Lot ID")
    instructions = fields.Text(string="Instructions", compute='_get_product_shiping_instructions', inverse='_set_product_shiping_instructions')
    product_tracking = fields.Selection(related="product_id.tracking")
    image = fields.Binary(related='product_id.image_medium', nolabel=1)
    product_stock_code = fields.Char(related='product_id.default_code')
    stock_available = fields.Float("Stock Available", compute='available_loc_stock')
    loc_stock = fields.Char(string="Location", compute="loc_with_stock")
    location_barcode = fields.Char(string="Location ID")
    container_location = fields.Many2one('stock.location')
    stock_content_ids = fields.One2many('stock.content', 'move_id', string='Stock Contents')
    move_doc_name = fields.Char(string='Document',compute='get_move_doc_name')
    available_qty = fields.Integer(string='Available')
    so_id = fields.Many2one('sale.order', string="Link to Document")
    po_id = fields.Many2one('purchase.order', string="Link to Document")
    to_id = fields.Many2one('transfer.order', string="Link to Document")
    all_containers = fields.Integer(string='All containers', compute='get_all_container_qty')

    @api.depends('stock_container_ids.container_qty')
    def get_all_container_qty(self):
        for rec in self:
            if rec.stock_container_ids:
                for line in rec.stock_container_ids:
                    rec.all_containers += line.container_qty

    @api.multi
    @api.depends('picking_id.partner_id','picking_id.origin')
    def get_move_doc_name(self):
        for rec in self:
            if rec.picking_id.partner_id and rec.picking_id.origin:
                rec.move_doc_name = '[' + rec.picking_id.origin + ']' + ' ' + rec.picking_id.partner_id.name
            elif rec.picking_id.origin:
                rec.move_doc_name = rec.picking_id.origin
            elif rec.picking_id.partner_id:
                rec.move_doc_name = rec.picking_id.partner_id.name

    @api.onchange('location_barcode')
    def get_location_name(self):
        if self.location_barcode :
            location = self.env['stock.location'].search([('barcode','=',self.location_barcode)])
            if not location :
                raise UserError(_('Invalid Location ID.'))
            self.container_location  = location.id

    @api.depends('available_loc', 'stock_available')
    def loc_with_stock(self):
        if self.available_loc:
            location = self.available_loc
            name = location.name
            while location.location_id and location.usage != 'view':
                location = location.location_id
                name = location.name + "/" + name
            self.loc_stock = name + ' (' + str(int(self.stock_available)) + ')'

    @api.depends('available_loc')
    def available_loc_stock(self):
        if self.available_loc:
            quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),('location_id','=',self.available_loc.id)])
            total = 0.0
            for qt in quant:
                total += (qt.quantity - qt.reserved_quantity)
            self.stock_available = total

    @api.multi
    def available_stock_qty(self):
        for rec in self:
            sub_total = 0.0
            if rec.product_id:
                quant = self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),('location_id.usage','=','internal')])
                for qt in quant:
                    sub_total += (qt.quantity - qt.reserved_quantity)
            return sub_total

    @api.depends('product_id')
    def get_product_name(self):
        for record in self:
            if record.product_id:
                product_full_name = record.product_id.full_name
                if record.product_id.default_code:
                    product_default_code = '['+ record.product_id.default_code + ']'
                    record.product_name = product_full_name.replace(product_default_code,'')
                else:
                    record.product_name = product_full_name

    product_name = fields.Char(compute='get_product_name', store=True)

    def _search_picking_for_assignation(self):
        self.ensure_one()
        route_id = False
        carrier_id = False
        if self.sale_line_id.route_id:
            route_id = self.sale_line_id.route_id.id
        if self.sale_line_id.carrier_id:
            carrier_id = self.sale_line_id.carrier_id.id
        
        if self.sale_line_id.delivery_date:
            del_date = self.sale_line_id.delivery_date.strftime("%Y-%m-%d")
        else :
            del_date = None
        if self.picking_type_id.name == 'Delivery Orders':
            picking = self.env['stock.picking'].search([
                ('group_id', '=', self.group_id.id),
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_dest_id.id),
                ('picking_type_id', '=', self.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned']), 
                ('scheduled_date', '=', del_date),
                ('carrier_id','=', carrier_id),
                ('route_id','=', route_id)], limit=1)
        else:
            picking = self.env['stock.picking'].search([
                    ('group_id', '=', self.group_id.id),
                    ('location_id', '=', self.location_id.id),
                    ('location_dest_id', '=', self.location_dest_id.id),
                    ('picking_type_id', '=', self.picking_type_id.id),
                    ('printed', '=', False),
                    ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
        return picking


    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        for move in self:
            recompute = False
            picking = move._search_picking_for_assignation()
            if picking:
                if picking.partner_id.id != move.partner_id.id or picking.origin != move.origin:
                    # If a picking is found, we'll append `move` to its move list and thus its
                    # `partner_id` and `ref` field will refer to multiple records. In this
                    # case, we chose to  wipe them.
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            move._assign_picking_post_process(new=recompute)
            # If this method is called in batch by a write on a one2many and
            # at some point had to create a picking, some next iterations could
            # try to find back the created picking. As we look for it by searching
            # on some computed fields, we have to force a recompute, else the
            # record won't be found.
            if recompute:
                move.recompute()
            if self.picking_type_id.name == 'Delivery Orders':
                if self.sale_line_id.delivery_date:
                    del_date = self.sale_line_id.delivery_date.strftime("%Y-%m-%d")
                picking.write({'scheduled_date': del_date})
        return True

    def _assign_picking_post_process(self, new=False):
        pass

    def _get_new_picking_values(self):
        """ Prepares a new picking for this move as it could not be assigned to
        another picking. This method is designed to be inherited. """
        if self.picking_type_id.name == 'Delivery Orders':
            if self.sale_line_id.delivery_date:
                del_date = self.sale_line_id.delivery_date.strftime("%Y-%m-%d")
            else : 
                del_date = None
            values = {
                'origin': self.origin,
                'company_id': self.company_id.id,
                'move_type': self.group_id and self.group_id.move_type or 'direct',
                'partner_id': self.partner_id.id,
                'picking_type_id': self.picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'route_id':self.sale_line_id.route_id.id or False,
                'scheduled_date':del_date,
                'carrier_id':self.sale_line_id.carrier_id.id or False,
                }
            return values
        return {
            'origin': self.origin,
            'company_id': self.company_id.id,
            'move_type': self.group_id and self.group_id.move_type or 'direct',
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
              }

    res_stock_so_id = fields.Many2one("sale.order.line", compute="_get_reserved_sale_line", store=True) 
 
    @api.depends('sale_line_id')
    def _get_reserved_sale_line(self):
        for line in self:
            if line.picking_type_id.name == 'Reserve Stock Transfers':
                line.res_stock_so_id = line.sale_line_id.id
            else:
                line.res_stock_so_id = False

    @api.multi
    def create_products_contents(self):
        if self.transfer_now <= 0:
            raise UserError(_('Transfer now quantity can not be less than one.'))
        if self.transfer_now > self.product_uom_qty:
            raise UserError(_('You can not transfer product more than required.'))
        container_obj = self.env['stock.container']
        content_obj = self.env['stock.content']
        container = container_obj.search([('container_barcode', '=', self.container_barcode)])
        content = content_obj.search([('move_id','=',self.id),
                                                    ('product_id','=',self.product_id.id),
                                                    ('container_barcode','=',self.container_barcode),
                                                    ('container_type','=',self.container_type.id),
                                                    ('location_barcode','=',self.location_barcode)])
        if content:
            if self.product_uom_qty < (content.contents_qty + self.transfer_now):
                raise UserError(_('Total contents Qty can not be greater than Required Qty.'))
            qty = self.transfer_now + content.contents_qty
            content.write({'contents_qty': qty})
            container.write({'est_weight': container.est_weight + self.product_id.weight*self.transfer_now})

        else:
            content_ids = self.env['stock.content'].search([('move_id','=',self.id),
                                                        ('product_id','=',self.product_id.id)])
            if content_ids:
                sub_total = 0
                for line in content_ids:
                    sub_total+= line.contents_qty
                if self.product_uom_qty < (sub_total + self.transfer_now):
                    raise UserError(_('Total transferred Qty can not be greater than Required Qty.'))
            if self.serial_no:
                self.serial_no.is_moved = True
                self.serial_no = False
            if container:
                values = {
                          'move_id':self.id,
                          'picking_id': self.picking_id.id,
                          'product_id': self.product_id.id,
                          'partner_id': self.partner_id.id,
                          'stock_container_id': container.id,
                          'container_barcode': container.container_barcode,
                          'container_type': container.container_type.id,
                          'location_barcode': self.location_barcode,
                          'location_id': self.container_location.id,
                          'contents_qty': self.transfer_now,
                          'is_product': True,
                          'stage' : 'active'
                        }
                if self.so_id:
                    values.update({'so_id':self.so_id.id})
                if self.po_id:
                    values.update({'po_id':self.po_id.id})
                if self.to_id:
                    values.update({'to_id':self.transfer_id.id})
                content_res = content_obj.create(values)
                data = {
                        'move_id': self.id,
                        'picking_id': self.picking_id.id,
                        'partner_id': self.partner_id.id,
                        'location_barcode': self.location_barcode,
                        'location_id': self.container_location.id,
                        # 'container_qty': self.transfer_now,
                        'desc' : self.instructions,
                        'stage' : 'active',
                        'est_weight': container.container_type.weight + container.est_weight + self.product_id.weight * self.transfer_now,
                        }
                if self.so_id:
                    data.update({'so_id':self.so_id.id})
                if self.po_id:
                    data.update({'po_id':self.po_id.id})
                if self.to_id:
                    data.update({'to_id':self.transfer_id.id})
                container.write(data)
            elif not container:
                vals = {
                        'move_id': self.id,
                        'picking_id': self.picking_id.id,
                        'so_id' : self.so_id.id,
                        'po_id':self.po_id.id,
                        'partner_id': self.partner_id.id,
                        'container_barcode': self.container_barcode,
                        'container_type': self.container_type.id,
                        'location_barcode': self.location_barcode,
                        'location_id': self.container_location.id,
                        'desc' : self.instructions,
                        'stage' : 'active'
                        }
                if self.so_id:
                    vals.update({'so_id':self.so_id.id})
                if self.po_id:
                    vals.update({'po_id':self.po_id.id})
                if self.to_id:
                    vals.update({'to_id':self.transfer_id.id})
                container_res = container_obj.create(vals)
                values = {
                        'move_id':self.id,
                        'picking_id': self.picking_id.id,
                        'product_id': self.product_id.id,
                        'partner_id': self.partner_id.id,
                        'stock_container_id': container_res.id,
                        'container_barcode': self.container_barcode,
                        'container_type': self.container_type.id,
                        'location_barcode': self.location_barcode,
                        'location_id': self.container_location.id,
                        'contents_qty': self.transfer_now,
                        'is_product' : True,
                        }
                if self.so_id:
                    values.update({'so_id':self.so_id.id})
                if self.po_id:
                    values.update({'po_id':self.po_id.id})
                if self.to_id:
                    values.update({'to_id':self.transfer_id.id})
                content = content_obj.create(values)
                container_res.write({'est_weight':container_res.container_type.weight + container_res.est_weight + self.product_id.weight*self.transfer_now})
        if self.transfer_now:
            self.transfer_now = False
        if self.serial_no:
           self.serial_no = False
        if self.container_barcode:
            self.container_barcode = False
        if self.container_type:
            self.container_type = False
        if self.location_barcode:
            self.location_barcode = False
        if self.container_location:
            self.container_location = False

    @api.multi
    def update_picking_states(self):
        blank_list = []
        for rec in self:
            blank_list.append(self.env['stock.picking.states'].search([('name','=','MOVE')]).id)
            res = rec.picking_id.write({'status': [(6,0, blank_list)] })
            return res

    @api.multi
    def generate_container_barcode(self):
        return True

    @api.model
    def create(self,vals):
        if vals.get('sale_line_id'):
            sol_id = self.env['sale.order.line'].search([('id','=',vals['sale_line_id'])]) 
            so_id = self.env['sale.order'].search([('id','=',sol_id.order_id.id)])
            vals['so_id'] = so_id.id
        if vals.get('purchase_line_id'):
            pol_id = self.env['purchase.order.line'].search([('id','=',vals['purchase_line_id'])]) 
            po_id = self.env['purchase.order'].search([('id','=',pol_id.order_id.id)])
            vals['po_id'] = po_id.id
        if vals.get('transfer_id'):
            to_id = self.env['transfer.order'].search([('id','=',vals['transfer_id'].id)])
            vals['to_id'] = to_id.id
        res = super(StockMove, self).create(vals)
        return res

    stock_container_ids = fields.One2many('stock.container', 'move_id', related='picking_id.stock_container_ids')

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_stock_move_line_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_stock_move_line_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
