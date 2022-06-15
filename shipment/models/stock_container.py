from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockContainer(models.Model):
    _name = "stock.container"
    _description = "Container"

    name = fields.Char(string='Container Name', compute='_get_container_name', store=True)
    dash_icon = fields.Char(string="icon",default='fas fa-box')
    state  = fields.Selection([('active', 'ACTIVE'),('inactive', 'INACTIVE'), ('absolete','ABSOLETE')], required=True, index=True, default='active')
    sequence = fields.Integer(string='Sequence')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_container_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_container_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
    
    @api.depends('container_type')
    def _get_container_name(self):
        for record in self:
            if record.container_type:
                record.name = record.container_type.name

    @api.onchange('stage')
    def set_picking_states(self):
        if self.stage:
            stage_list = []
            for line in self:
                if line.stage:
                    stage_list.append(line.stage)

    @api.onchange('container_type')
    def get_contianer_dimensions(self):
        if self.container_type.dim1:
            self.dim1 = self.container_type.dim1
        if self.container_type.dim2:
            self.dim2 = self.container_type.dim2
        if self.container_type.dim3:
            self.dim3 = self.container_type.dim3

    # @api.depends('stock_content_ids','stock_content_ids.contents_qty')
    # def get_product_qty_in_container(self):
    #     for rec in self:
    #         if rec.stock_content_ids:
    #             for line in rec.stock_content_ids:
    #                 rec.container_qty += line.contents_qty

    move_id = fields.Many2one('stock.move')
    container_qty = fields.Integer(string='Quantity')
    image = fields.Binary(string="Container Tyoe Icon", related="container_type.icon.image")
    product_id = fields.Many2one('product.product', string="Product", help="Container name in release and ship tab in container view")
    container_barcode = fields.Char(string='Container ID')
    partner_id = fields.Many2one('res.partner', string='Customer')
    picking_id = fields.Many2one('stock.picking', string='Shipment')
    location_barcode = fields.Char(string="Location ID")
    location_id = fields.Many2one('stock.location', string='Container Location')
    container_type = fields.Many2one('stock.container.type', string='Container')
    new_container_barcode = fields.Char(string='Container ID')
    new_container_type = fields.Many2one('stock.container.type', string='Container')
    stock_container_id = fields.Many2one('stock.container', string='Container')
    stock_content_ids = fields.One2many('stock.content', 'stock_container_id', string='Content')
    parent_id = fields.Many2one('stock.container', string='Related Container')
    child_ids = fields.One2many('stock.container', 'parent_id', string='Container')
    dim1 = fields.Float(string='Dimension 1')
    dim2 = fields.Float(string='Dimenstion 2')
    dim3 = fields.Float(string='Dimenstion 3')
    est_weight = fields.Float(string='Estimated Weight')
    act_weight = fields.Float(string='Actual Weight')
    moved_product = fields.Integer(string='Moved')
    change_dest_location_id = fields.Many2one('stock.location', string="New Location")
    shipping_warning = fields.Char(string="Instrucion")
    new_location_id = fields.Many2one('stock.location', string="Location")
    new_location_barcode = fields.Char(string="Location ID")
    desc = fields.Text(string="Description")
    stage = fields.Selection([('active', 'ACTIVE'),
                              ('inactive', 'INACTIVE'),
                              ('absolete', 'ABSOLETE')],string='Stage', default='assign')
    move_comments = fields.Text(string="Comment")

    container_function = fields.Char(string="Function")
    container_for = fields.Char(string="For")
    document = fields.Char(string="Document")
    assigned = fields.Many2one('res.users',string="Assigned")
    full_name = fields.Char(string="Container full name",readonly=True,compute='get_container_full_name')
    new_container_name = fields.Char(string='Move to Container', compute='get_new_container_and_location')
    new_location_name = fields.Char(string='Move to Location',compute='get_new_container_and_location')
    so_id = fields.Many2one('sale.order', string='Link to Document')
    po_id = fields.Many2one('purchase.order', string='Link to Document')
    to_id = fields.Many2one('transfer.order', string='Link to Document')

    @api.depends('new_container_barcode','new_container_type','new_location_barcode','new_location_id')
    def get_new_container_and_location(self):
        for rec in self:
            if rec.new_container_barcode and rec.new_container_type:
                rec.new_container_name = '[' + rec.new_container_barcode + ']'
            if rec.new_location_barcode and rec.new_location_id:
                rec.new_location_name = '[' + rec.new_location_barcode + ']'

    @api.multi
    @api.depends('container_type','container_barcode')
    def get_container_full_name(self):
        for rec in self:
            full_name = ' '
            if rec.container_barcode and rec.container_type:
                full_name =  '[' + rec.container_barcode + ']' + ' ' + rec.container_type.name
            if rec.container_type.dim1 and not rec.container_type.dim2 and not rec.container_type.dim3:
                full_name += ',' + ' ' + str(rec.container_type.dim1)
            if rec.container_type.dim2 and not rec.container_type.dim1 and not rec.container_type.dim3:
                full_name += ',' + ' ' + str(rec.container_type.dim2)
            if rec.container_type.dim3 and not rec.container_type.dim2 and not rec.container_type.dim1:
                full_name += ',' + ' ' + str(rec.container_type.dim3)
            if rec.container_type.dim1 and rec.container_type.dim2 and rec.container_type.dim3:
                full_name += ',' + ' ' + str(rec.container_type.dim1) + ' ' + 'x' + ' ' + str(rec.container_type.dim2) + ' ' + 'x' + ' ' + str(rec.container_type.dim3)
            elif rec.container_type.dim1 and rec.container_type.dim2:
                full_name += ',' + ' ' + str(rec.container_type.dim1) + ' ' + 'x' + ' ' + str(rec.container_type.dim2)
            elif rec.container_type.dim2 and rec.container_type.dim3:
                full_name += ',' + ' ' + str(rec.container_type.dim2) + ' ' + 'x' + ' ' + str(rec.container_type.dim3)
            elif rec.container_type.dim1 and rec.container_type.dim3:
                full_name += ',' + ' ' + str(rec.container_type.dim1) + ' ' + 'x' + ' ' + str(rec.container_type.dim3)
            rec.full_name = full_name
            rec.name = full_name

    @api.onchange('new_location_barcode','new_container_barcode')
    def get_new_container_location_name(self):
        for rec in self:
            if rec.new_location_barcode:
                location = self.env['stock.location'].search([('barcode', '=', rec.new_location_barcode)])
                if location:
                    rec.new_location_id = location.id
                else:
                    raise UserError(_('Invalid Location ID.'))
            if rec.new_container_barcode:
                container = self.env['stock.container'].search([('container_barcode', '=', self.new_container_barcode)])
                if container:
                    rec.new_container_type = container.container_type.id



    def move_container_to_container(self):
        container_obj = self.env['stock.container']
        content_obj = self.env['stock.content']
        old_container = container_obj.search([('container_barcode', '=', self.container_barcode)])
        container = container_obj.search([('container_barcode', '=', self.new_container_barcode)])
        if container:
            if container.stage == 'release' or container.stage == 'ship':
                raise UserError(_('You can not move container into those container that is released or shipped.'))
        if self.container_barcode == self.new_container_barcode: # Change container Location..
            self.location_id = self.new_location_id
            self.location_barcode = self.new_container_barcode
            for line in self.stock_content_ids:
                if line.location_id:
                    line.location_id = self.new_location_id
                    line.location_barcode = self.new_location_barcode
            for rec in self.child_ids:
                if rec.location_id:
                    rec.location_id = self.new_location_id
                    rec.location_barcode = self.new_location_barcode
            if self.new_container_barcode:
                self.new_container_barcode = False
            if self.new_container_type:
                self.new_container_type = False
            if self.new_location_barcode:
                self.new_location_barcode = False
            if self.new_location_id:
                self.new_location_id = False
            return True
        if container:
            values = {
                      'picking_id': self.picking_id.id,
                      'container_id': self.id,
                      'partner_id': self.partner_id.id,
                      'stock_container_id': container.id,
                      'container_barcode': container.container_barcode,
                      'container_type': container.container_type.id,
                      'location_barcode': self.new_location_barcode,
                      'location_id': self.new_location_id.id,
                      'contents_qty': 1,
                      'is_product': False
                    }
            content_res = content_obj.create(values)
            vals = ({
                    'picking_id': self.picking_id.id,
                    'partner_id': self.partner_id.id,
                    'location_barcode': self.new_location_barcode,
                    'location_id': self.new_location_id.id,
                    'desc': self.move_comments,
                    'est_weight': container.container_type.weight + self.est_weight,
                    })
            if self.so_id:
                vals.update({'so_id':self.so_id.id})
            if self.po_id:
                vals.update({'po_id':self.po_id.id})
            if self.to_id:
                vals.update({'to_id':self.to_id.id})
            container.write(vals)
            old_container.write({
                                'parent_id': container.id,
                                'stage' : 'active',
                                'location_barcode': self.new_location_barcode,
                                'location_id': self.new_location_id.id,
                                })

        elif not container:
            vals = {
                    'picking_id': self.picking_id.id,
                    'partner_id': self.partner_id.id,
                    'container_barcode': self.new_container_barcode,
                    'container_type': self.new_container_type.id,
                    'location_barcode': self.new_location_barcode,
                    'location_id': self.new_location_id.id,
                    'stage' : 'active'
                    }
            if self.so_id:
                vals.update({'so_id':self.so_id.id})
            if self.po_id:
                vals.update({'po_id':self.po_id.id})
            if self.to_id:
                vals.update({'to_id':self.to_id.id})
            container_res = container_obj.create(vals)
            values = {
                    'picking_id': self.picking_id.id,
                    'container_id': self.id,
                    'partner_id': self.partner_id.id,
                    'stock_container_id': container_res.id,
                    'container_barcode': self.new_container_barcode,
                    'container_type': self.new_container_type.id,
                    'location_barcode': self.new_location_barcode,
                    'location_id': self.new_location_id.id,
                    'contents_qty': 1,
                    'is_product' : False
                    }
            content = content_obj.create(values)
            old_container.write({
                                'parent_id': container_res.id,
                                'location_barcode': self.new_location_barcode,
                                'location_id': self.new_location_id.id,
                                })
            container_res.write({'est_weight':container_res.container_type.weight + self.est_weight})
        if self.new_container_barcode:
            self.new_container_barcode = False
        if self.new_container_type:
            self.new_container_type = False
        if self.new_location_barcode:
            self.new_location_barcode = False
        if self.new_location_id:
            self.new_location_id = False
        if self.move_comments:
            self.move_comments = False
    
    def get_barcode(self):
        return True

    def release_container(self):
        total = 0
        # if self.picking_id._check_backorder():
        #     return self.picking_id.action_generate_backorder_wizard()
        if self.stage == 'release' or self.stage == 'ship':
            raise UserError(_('You can not repeat action.'))

        if self.child_ids: # If container will be inside of the container 
            for line in self.child_ids:
                total += line.stock_content_ids.contents_qty
                line.stage = 'release'
            self.stage = 'release'
            self.child_ids.stock_content_ids.move_id.release -= total

        if self.stock_content_ids and not self.child_ids: # If container will be independent
            for line in self.stock_content_ids:
                line.stage = 'release'
                total += line.contents_qty
            self.stage = 'release'
            self.stock_content_ids.move_id.release -= total

        if self.stock_container_id:
            self.stock_container_id = False
        if self.dim1:
            self.dim1 = False
        if self.dim2:
            self.dim2 = False
        if self.dim3:
            self.dim3 = False
        if self.est_weight:
            self.est_weight = False
        if self.act_weight:
            self.act_weight = False
        return True

    def ship_container(self):
        total = 0
        if self.stage == 'ship':
            raise UserError(_('You can not ship container again.'))
        if self.stock_container_id:
            if self.child_ids: # If container will be inside of the container
                for line in self.child_ids:
                    total += line.stock_content_ids.contents_qty
                    line.stage = 'ship'
                self.stage = 'ship'
                self.child_ids.stock_content_ids.move_id.ship -= total
            
            if self.stock_content_ids and not self.child_ids: # If container will be independent
                for line in self.stock_content_ids:
                    line.stage = 'ship'
                    total += line.contents_qty
                self.stage = 'ship'
                self.stock_content_ids.move_id.release -= total

            if self.stock_container_id:
                self.stock_container_id = False
            if self.dim1:
                self.dim1 = False
            if self.dim2:
                self.dim2 = False
            if self.dim3:
                self.dim3 = False
            if self.est_weight:
                self.est_weight = False
            if self.act_weight:
                self.act_weight = False
        return True

    def get_label(self):
        return True

    def get_documents(self):
        return True

    def get_packlist(self):
        return True
