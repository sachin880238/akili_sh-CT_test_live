from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockContent(models.Model):
    _name = "stock.content"
    _description = 'Content'

    name = fields.Char(string="Contents", compute='_get_content_name')

    @api.depends('product_id', 'container_id')
    def _get_content_name(self):
        for record in self:
            if record.is_product:
                name = record.product_id.full_name
                record.name = name
            elif not record.is_product:
                if record.container_id:
                    name = '[' + record.container_id.container_barcode + ']' + ' ' + record.container_id.container_type.name
                    record.name = name

    move_id = fields.Many2one('stock.move')
    picking_id = fields.Many2one('stock.picking', string="Shipment ID")
    product_id = fields.Many2one('product.product')
    image = fields.Binary(related='product_id.image_medium', nolabel=1)
    cont_image = fields.Binary(related='container_id.container_type.icon.image')
    product_stock_code = fields.Char(related='product_id.default_code')
    partner_id = fields.Many2one('res.partner', string='Customer')
    stock_container_id = fields.Many2one('stock.container')
    container_id = fields.Many2one('stock.container')
    container_code = fields.Char(related='container_id.container_barcode')
    container_barcode = fields.Char(string='Container ID')
    container_type = fields.Many2one('stock.container.type', string='Container')
    location_barcode = fields.Char(string='Location ID')
    location_id = fields.Many2one('stock.location', string='Location')
    contents_qty = fields.Integer(string='Contents')
    serial_no = fields.Many2one('stock.production.lot',string='Serial ID')
    new_container_barcode = fields.Char(string='Container ID')
    new_container_type = fields.Many2one('stock.container.type', string='Container')
    new_location_barcode = fields.Char(string='Location ID')
    new_location_id = fields.Many2one('stock.location', string='Location')
    instructions = fields.Text(related='product_id.packing_warn_msg', string='Instructions')
    product_tracking = fields.Selection(related="move_id.product_tracking")
    transfer_now = fields.Integer(string="Transfer Now")
    container_location_id = fields.Many2one('stock.location', readonly="1", string="Location")
    is_product = fields.Boolean(string="Is Product", help="To identify whether it is product or container")
    lot_id = fields.Many2one('stock.production.lot', string="Lot Id")    
    stock_location = fields.Many2one('stock.location', string='Stock Location')
    remove_now = fields.Integer(string="Remove Now")
    restock_now = fields.Integer(string="Restock Now")
    sequence = fields.Integer(string="Sequence")
    container_name = fields.Char(string="Container",compute='get_container_location_doc_name', store=True)
    document_name = fields.Char(string="Document",compute='get_container_location_doc_name', store=True)
    location_name = fields.Char(string="Location",compute='get_container_location_doc_name', store=True)
    so_id = fields.Many2one('sale.order', string='Link to Document')
    po_id = fields.Many2one('purchase.order', string='Link to Document')
    
    @api.onchange('new_location_barcode','new_container_barcode')
    def get_new_content_location_name(self):
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

    @api.depends('container_id')
    def get_container_location_doc_name(self):
        for record in self:
            if record.container_type and record.container_barcode:
                record.container_name = '[' + record.container_barcode + ']' + ' ' + record.container_type.name
            if record.picking_id.origin and record.picking_id.parent_id:
                record.document_name = '[' + record.picking_id.origin + ']' + ' ' + record.picking_id.parent_id.name
            else:
                record.document_name = record.picking_id.parent_id.name
            if record.location_id and record.location_id.barcode:
                record.location_name = '[' + record.location_id.barcode + ']' + ' ' + record.location_id.name
            else:
                record.location_name = record.location_id.name

    @api.depends('product_id')
    def get_product_container_icon(self):
        self.self_container = True
        
    self_container = fields.Boolean(string="Is Container", default=False, compute='get_product_container_icon')

    @api.model
    def create(self, vals):
        res = super(StockContent, self).create(vals)
        if res.move_id:
            move_id = res.move_id
            move_line_obj = self.env['stock.move.line']
            move_line_id = move_line_obj.search([('move_id','=',res.move_id.id),('location_id','=', move_id.available_loc.id)])
            total_reserved = 0.0
            for mv_line in move_line_obj.search([('move_id','=',res.move_id.id)]):
                total_reserved += mv_line.product_uom_qty
            total_reserved += vals['contents_qty']
            if not move_line_id:
                values = {
                  'move_id':move_id.id,
                  'location_id':move_id.available_loc.id,
                  'product_id':res.product_id.id,
                  'location_dest_id': move_id.location_dest_id.id,
                  'state':'assigned',
                  'product_uom_id':move_id.product_uom.id
                       }
                move_line_id = move_line_obj.create(values)
                if move_id.product_uom_qty == total_reserved:
                    move_id.write({'state':'assigned'})
                else:
                    move_id.write({'state':'partially_available'})
                move_line_id.write({'product_uom_qty':vals['contents_qty']})
                    
            else:
                reserve_qty = move_line_id.product_uom_qty + vals['contents_qty']
                if move_id.product_uom_qty == total_reserved:
                    move_id.write({'state':'assigned'})
                else:
                    move_id.write({'state':'partially_available'})
                result = move_line_id.write({'product_uom_qty': reserve_qty})
        return res

    # @api.model
    # def write(self, vals):
    #     res = super(StockContent, self).write(vals)
    #     move_id = res.move_id
    #     move_line_obj = self.env['stock.move.line']
    #     move_line_id = move_line_obj.search([('move_id','=',res.move_id.id),('location_id','=', vals['location_id'])])
    #     total_reserved = 0.0
    #     for mv_line in move_line_obj.search([('move_id','=',res.move_id.id)]):
    #         total_reserved += mv_line.product_uom_qty
    #     total_reserved += vals['contents_qty']
    #     reserve_qty = move_line_id.product_uom_qty + vals['contents_qty']
    #     if move_id.product_uom_qty == total_reserved:
    #         move_id.write({'state':'assigned'})
    #     else:
    #         move_id.write({'state':'partially_available'})
    #     result = move_line_id.write({'product_uom_qty': reserve_qty})
    #     return res

    @api.multi
    def generate_barcode(self):
        return True

    def transfer_product(self):
        container_obj = self.env['stock.container']
        old_container = container_obj.search([('container_barcode', '=', self.container_barcode)]) 
        container = container_obj.search([('container_barcode', '=', self.new_container_barcode)])
        content_obj = self.env['stock.content']
        if self.is_product:
            if self.transfer_now <= 0:
                raise UserError(_('Transfer now quantity can not be less than one.'))
            if self.transfer_now > self.contents_qty:
                raise UserError(_('You can not move product more than available.'))
            if self.transfer_now < self.contents_qty:
                if container:
                    self.contents_qty = self.contents_qty - self.transfer_now
                    values = {
                              'picking_id': self.picking_id.id,
                              'product_id': self.product_id.id,
                              'partner_id': self.partner_id.id,
                              'stock_container_id': container.id,
                              'container_barcode': container.container_barcode,
                              'container_type': container.container_type.id,
                              'location_barcode': self.new_location_barcode,
                              'location_id': self.new_location_id.id,
                              'contents_qty': self.transfer_now,
                              'is_product': self.is_product
                            } 
                    content_obj.create(values)
                    container.write({
                                    'picking_id': self.picking_id.id,
                                    'partner_id': self.partner_id.id,
                                    'location_barcode': self.new_location_barcode,
                                    'location_id': self.new_location_id.id,
                                    })
                elif not container:
                    vals={
                            'partner_id': self.partner_id.id,
                            'picking_id': self.picking_id.id,
                            'container_barcode': self.new_container_barcode,
                            'container_type': self.new_container_type.id,
                            'location_barcode': self.new_location_barcode,
                            'location_id': self.new_location_id.id,
                        }
                    container_id = container_obj.create(vals)
                    self.contents_qty = self.contents_qty - self.transfer_now
                    values = {
                              'picking_id': self.picking_id.id,
                              'product_id': self.product_id.id,
                              'partner_id': self.partner_id.id,
                              'stock_container_id': container_id.id,
                              'container_barcode': container_id.container_barcode,
                              'container_type': container_id.container_type.id,
                              'location_barcode': self.new_location_barcode,
                              'location_id': self.new_location_id.id,
                              'contents_qty': self.transfer_now,
                              'is_product': self.is_product
                            } 
                    content_obj.create(values)
            elif self.transfer_now == self.contents_qty:
                if container:
                    self.stock_container_id = container.id
                    self.container_barcode = container.container_barcode
                    self.container_type = container.container_type.id
                    self.location_id = self.new_location_id.id
                    self.location_barcode = self.new_location_barcode
                    self.serial_no = self.serial_no.id or False
                    old_container.write({
                                    'picking_id': False,
                                    'partner_id': False,
                                    'location_barcode': False,
                                    'location_id': False,
                                    })
                    container.write({
                                    'picking_id': self.picking_id.id,
                                    'partner_id': self.partner_id.id,
                                    'location_barcode': self.new_location_barcode,
                                    'location_id': self.new_location_id.id,
                                    })
                elif not container:
                    vals={
                            'partner_id': self.partner_id.id,
                            'picking_id': self.picking_id.id,
                            'container_barcode': self.new_container_barcode,
                            'container_type': self.new_container_type.id,
                            'location_barcode': self.new_location_barcode,
                            'location_id': self.new_location_id.id,
                            }
                    container_id = container_obj.create(vals)
                    self.container_barcode = self.new_container_barcode
                    self.container_type = self.new_container_type.id
                    self.location_id = self.new_location_id.id
                    self.location_barcode = self.new_location_barcode
                    self.serial_no = self.serial_no.id or False
                    self.stock_container_id = container_id.id
                    old_container.write({
                                    'picking_id': False,
                                    'partner_id': False,
                                    'location_barcode': False,
                                    'location_id': False,
                                    })
        elif not self.is_product:
            if container:
                self.stock_container_id = container.id
                self.container_barcode = container.container_barcode
                self.container_type = container.container_type.id
                self.location_id = self.new_location_id.id
                self.location_barcode = self.new_location_barcode
                self.container_id.parent_id = container
                container.write({
                                'picking_id': self.picking_id.id,
                                'partner_id': self.partner_id.id,
                                'location_barcode': self.new_location_barcode,
                                'location_id': self.new_location_id.id,
                                })
                old_container.write({
                                    'picking_id': False,
                                    'partner_id': False,
                                    'location_barcode': False,
                                    'location_id': False,
                                    })

            elif not container:
                vals = {
                        'picking_id': self.picking_id.id,
                        'partner_id': self.partner_id.id,
                        'container_barcode': self.new_container_barcode,
                        'container_type': self.new_container_type.id,
                        'location_barcode': self.new_location_barcode,
                        'location_id': self.new_location_id.id,
                        }
                container_res = container_obj.create(vals)
                
                self.container_barcode = self.new_container_barcode
                self.container_type = self.new_container_type.id
                self.location_id = self.new_location_id.id
                self.location_barcode = self.new_location_barcode
                self.stock_container_id = container_res.id
                self.container_id.parent_id = container_res 
                old_container.write({
                                'picking_id': False,
                                'partner_id': False,
                                'location_barcode': False,
                                'location_id': False,
                                })
        self.transfer_now = 0
        self.new_container_barcode = False
        self.new_container_type = False
        self.new_location_id = False
        self.new_location_barcode = False
