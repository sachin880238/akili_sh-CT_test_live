# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp
import logging

from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    truckload_qty = fields.Integer(string='Truckload Quantity')
    hts_code = fields.Many2one('hts.description', string="HTS Code")
    hts_desc = fields.Char(related='hts_code.description', string="HTS Description")
    container_qty = fields.Integer(string="Container Quantity")
    
    status = fields.Selection([
        ('draft', 'DRAFT'),
        ('private', 'PRIVATE'),
        ('public', 'PUBLIC'),
        ('inactive', 'INACTIVE')], required="true", default="draft")
    unpublish_product = fields.Boolean(default=True)
    prod_template_name = fields.Char('Template')
    primary_vendor = fields.Many2one('res.partner', string='Vendor Primary', compute='compute_primary_vendor')
    vendor_stock_code = fields.Char(string='Vendor Stock ID', compute='compute_primary_vendor')
    vendor_description = fields.Text(string='Vendor Description', compute='compute_primary_vendor')
    price = fields.Float(string='Price')
    date_start = fields.Date(string='Price Effective', compute='compute_primary_vendor')
    date_end = fields.Date(string='Price Expires', compute='compute_primary_vendor')
    min_qty = fields.Integer(string='Minimum Quantity', compute='compute_primary_vendor')
    preferred = fields.Integer(string='Preferrd Quantity', compute='compute_primary_vendor')
    multiple = fields.Integer(string='Quantity Multiple', compute='compute_primary_vendor')
    delay = fields.Integer(string='Days to Ship', compute='compute_primary_vendor')
    volume = fields.Float('Volume', help="The volume in m3.", compute='_compute_volume', readonly=False)
    source_ids = fields.One2many('product.sources', 'product_id', string='Source')

    @api.constrains('default_code')
    def _check_default_code(self):
        code = self.search([('default_code','=',self.default_code)])
        if len(code) > 1:
            raise ValidationError(_("Stock ID must be unique!"))


    @api.depends('dim1','dim2','dim3')
    def _compute_volume(self):
        for rec in self:
            if rec.dim1 and rec.dim2:
                rec.volume = rec.dim1 * rec.dim2
            if rec.dim1 and rec.dim2 and rec.dim3:
                rec.volume = rec.dim1 * rec.dim2 * rec.dim3 

    @api.multi
    def compute_primary_vendor(self):
        for rec in self:
            vendor_id = self.env["product.supplierinfo"].search([('product_id','=',rec.id),('primary_vendor','=',True)])
        for line in vendor_id :
            self.primary_vendor = line.name
            self.vendor_stock_code = line.stock
            self.vendor_description = line.description
            # self.price = line.price
            self.date_start = line.date_start
            self.date_end = line.date_end
            self.min_qty = line.min_qty
            self.preferred = line.preferred
            self.multiple = line.multiple
            self.delay = line.delay

    def get_code(self, values):
        code = ''
        attr_obj = self.env['product.template.attribute.line']
        for attr in self.attribute_value_ids:
            if attr in values:
                variant_id = attr_obj.search([('product_tmpl_id','=',self.product_tmpl_id.id),('attribute_id','=',attr.attribute_id.id)])
                if variant_id.before:
                    deff = len(variant_id.before)
                    if deff == 1:
                        if variant_id.before == "#":
                            code += str(' ')+attr.name
                        else:
                            code += variant_id.before+attr.name
                    elif deff > 1:
                        if variant_id.before[0] == "#" and variant_id.before[deff-1] == "#":
                            code += str(' ')+variant_id.before[1:deff-1]+str(' ')+attr.name
                        if variant_id.before[0] == "#" and variant_id.before[deff-1] != "#":
                            code += str(' ')+variant_id.before[1:deff]+attr.name
                        if variant_id.before[0] != "#" and variant_id.before[deff-1] == "#":
                            code +=variant_id.before[0:deff-1]+str(' ')+attr.name
                    if variant_id.after:
                        deff2 = len(variant_id.after)
                        if deff2 == 1:
                            if variant_id.after == "#":
                                code += str(' ') 
                            else:
                                code += variant_id.after
                        elif deff2 > 1:
                            if variant_id.after[0] == "#" and variant_id.after[deff2-1] == "#":
                                code += str(' ')+variant_id.after[1:deff2-1]+str(' ')
                            if variant_id.after[0] == "#" and variant_id.after[deff2-1] != "#":
                                code += str(' ')+variant_id.after[1:deff2]
                            if variant_id.after[0] != "#" and variant_id.after[deff2-1] == "#":
                                code +=variant_id.after[0:deff2-1]+str(' ')
                elif variant_id.after:
                    deff2 = len(variant_id.after)
                    if deff2 == 1:
                        if variant_id.after == "#":
                            code += str(' ')+attr.name
                        else:
                            code += variant_id.after+attr.name
                    elif deff2 > 1:
                        if variant_id.after[0] == "#" and variant_id.after[deff2-1] == "#":
                            code += str(' ')+variant_id.after[1:deff2-1]+str(' ')+attr.name
                        if variant_id.after[0] == "#" and variant_id.after[deff2-1] != "#":
                            code += str(' ')+variant_id.after[1:deff2]+attr.name
                        if variant_id.after[0] != "#" and variant_id.after[deff2-1] == "#":
                            code +=variant_id.after[0:deff2-1]+str(' ')+attr.name
                if not variant_id.after and not variant_id.before:
                    code += str(' ')+attr.name
        return code

    def get_product_complete_name(self):
        for line in self:
            code = '' 
            if line.default_code:
                if line.default_code[0:1] != '[':
                    code = '['+ str(line.default_code)
                else:
                    code = line.default_code
                if line.default_code[len(line.default_code)-1:len(line.default_code)] != ']':
                    code += '] '
            code1 = '' 
            if line.attribute_value_ids:
                seq = []
                seq_attr = {}
                for line1 in line.product_tmpl_id.attribute_line_ids:
                    seq.append(line1.sequence)  
                    seq_attr[line1.sequence] = line1.value_ids 
                seq.sort()
                for sq in seq:
                    code1 += line.get_code(seq_attr[sq])
            if code1:
                code1 = "%s"%(code1)
            line.full_name = code + (line.name or line.product_tmpl_id.name) + code1
        return True 


    def get_product_line_name(self):
        for line in self:
            code = ''
            code1 = '' 
            if line.attribute_value_ids:
                seq = []
                seq_attr = {}
                for line1 in line.product_tmpl_id.attribute_line_ids:
                    seq.append(line1.sequence)  
                    seq_attr[line1.sequence] = line1.value_ids 
                seq.sort()
                for sq in seq:
                    code1 += line.get_code(seq_attr[sq])
            if code1:
                code1 = "%s"%(code1)
            line.line_name = code + (line.name or line.product_tmpl_id.name) + code1
        return True 
 
 
    name = fields.Char(
        string='Name',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=True
    )

    website_name = fields.Char(related='product_tmpl_id.website_name', string='Website Product Title')

    master_product = fields.Many2one('product.template', string='Master Product', compute="get_master_product")

    @api.multi
    def get_master_product(self):
        for rec in self :
            rec.master_product = rec.product_tmpl_id
            if rec.qty_available == rec.virtual_available:
                rec.inventory_reserved = False
            if rec.qty_available > rec.virtual_available:
                rec.inventory_reserved = rec.qty_available - rec.virtual_available
 
    full_name = fields.Char(compute=get_product_complete_name,  string="Full Name")
    line_name = fields.Char(compute=get_product_line_name,  string="Product")

    product_description = fields.Char(
            string='Product template description',
            required=False,
            readonly=False,
            index=False,
            default=None,
            help=False,
            translate=True
    )    


    # sales notebook

    warranty = fields.Float('Warranty')

    version = fields.Integer("Version")

    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits=dp.get_precision('Product Price'),
        help="Price at which the product is sold to customers.")

    sale_delay = fields.Float(
        'Customer Lead Time', default=0,
        help="Delivery lead time, in days. It's the number of days, promised to the customer, between the confirmation of the sales order and the delivery.")
 
    produce_delay = fields.Float(
        'Manufacturing Delay', default=0.0,
        help="Average lead time in days to manufacture this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added.")


    public_categ_ids = fields.Many2many('product.public.category', string='Website Product Category',
                                        help="The product will be available in each mentioned e-commerce category. Go to"
                                        "Shop > Customize and enable 'E-commerce categories' to view all e-commerce categories.")
    
    # optional_product_ids = fields.Many2many('product.product', 'product_product_optional_rel', 'src_id', 'dest_id',
    #                                         string='Optional Products', help="Optional Products are suggested "
    #                                         "whenever the customer hits *Add to Cart* (cross-sell strategy, "
    #                                         "e.g. for computers: warranty, software, etc.).")


    # alternative_product_ids = fields.Many2many('product.product', 'product_product_alternative_rel', 'src_id', 'dest_id',
    #                                            string='Alternative Products', help='Suggest alternatives to your customer'
    #                                            '(upsell strategy).Those product show up on the product page.')
    

    # accessory_product_ids = fields.Many2many('product.product', 'product_product_accessory_rel', 'src_id', 'dest_id',
    #                                          string='Accessory Products', help='Accessories show up when the customer'
    #                                         'reviews the cart before payment (cross-sell strategy).')

    available_in_pos = fields.Boolean(string='Available in POS', help='Check if you want this product to appear in the Point of Sale.', default=False)
    
    to_weight = fields.Boolean(string='To Weigh With Scale', help="Check if the product should be weighted using the hardware scale integration.")
    
    pos_categ_id = fields.Many2one(
        'pos.category', string='Point of Sale Category',
        help="Category used in the Point of Sale.")

    description_quote = fields.Text("Sales Notes")
    description_sale = fields.Text("Sales")
    pro_description_sale = fields.Html("Sales")
    sale_line_warn_msg = fields.Text("Sales Warning") 

    @api.multi
    def name_get(self):
        result = []
        for pro in self:
            result.append((pro.id, pro.full_name))
        return result

    @api.onchange('sale_line_warn_msg')
    def onchange_sale_line_warn_msg(self):
        if self.sale_line_warn_msg:
            self.sale_warn = 'warning' 
        else :
            self.sale_warn = 'no-message' 
        
    description = fields.Text("Sales Notes")
    product_team_id = fields.Many2one('crm.team', string='Product Team')

    # inventory

    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking", help="Ensure the traceability of a storable product in your warehouse.", default='none', required=True)
    
    sale_ok = fields.Boolean('Can be Sold', default=True)
    purchase_ok = fields.Boolean('Can be Purchased', default=True)

    can_be_expensed = fields.Boolean(string="Can be Expensed", help="Specify whether the product can be selected in an expense.")

    recurring_invoice = fields.Boolean('Subscription Product', 
                               help='If set, confirming a sale order with this product will create a subscription')


    life_time = fields.Integer(string='Product Life Time',
        help='Number of days before the goods may become dangerous and must not be consumed. It will be computed on the lot/serial number.')
    use_time = fields.Integer(string='Product Use Time',
        help='Number of days before the goods starts deteriorating, without being dangerous yet. It will be computed using the lot/serial number.')
    removal_time = fields.Integer(string='Product Removal Time',
        help='Number of days before the goods should be removed from the stock. It will be computed on the lot/serial number.')
    alert_time = fields.Integer(string='Product Alert Time',
        help='Number of days before an alert should be raised on the lot/serial number.')

    route_ids = fields.Many2many(
        'stock.location.route', 'stock_route_product_product', 'product_id', 'route_id', 'Routes',
        domain=[('product_selectable', '=', True)],
        help="Depending on the modules installed, this will allow you to define the route of the product: whether it will be bought, manufactured, MTO, etc.")

    hs_code = fields.Char(
        string='Hs code',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=True
    )
    
    description_pickingout = fields.Text('Description on Delivery Orders', translate=True)
 

    @api.onchange('product_type')
    def onchange_lang(self):
        if self.product_type in ['is_shipping', 'service']:
            self.type = 'service' 
        if self.product_type in ['consu', 'is_pallet', 'container']:
            self.type = 'consu' 
        if self.product_type in ['product','set','bundle']:
            self.type = 'product'  
        
    # shipping
    packing_category = fields.Selection(
        [
            ('bare', 'Bare'),
            ('alone', 'Alone'),
            ('flowable', 'Flowable'),
            ('flexible', 'Flexible'),
            ('rigid', 'Rigid'),
            ('enclosed', 'Boxed'),
            ('nestable', 'Nestable'),
            ('rollable', 'Rollable'),
            ('long', 'Long'),
            ('kit', 'Kit')

        ],
        string='Product Packaging Category',
        help=" - bare (ships without a container).\n"
             " - alone (ships in a dedicated container).\n"
             "- flowable (fills all space in container).\n"
             "- flexible (can conform to space but not as efficiently as flowable).\n"
             "- rigid (cannot conform to space but other products can fit within boundaries).\n"
             "- enclosed (item individually packaged within container, no other products can fit within boundaries).\n"
             "- nestable (rigid but items nest to reduce space).\n"
             "- rollable (flexible but wraps around rigid core).\n"
             "- long (requires container that is much longer in one dimension than others).\n"
             "- kit (set of products).\n")

    container_quantity = fields.Integer(
        string='Product Container Quantity', help="alone product will fit into container above")


    dedicated_container_id = fields.Many2one(
        'shipping.container', string='Product Container ID', help="Dedicated container for products that ship alone")


    product_surcharge = fields.Float(
        string='Product Surcharge', help="Charge assessed once for each product unit")
    
    line_surcharge = fields.Float(
        string='Product Orderline Surcharge', help="Charge assessed once for each orderline")

    weight_increment = fields.Float('Weight Increment')

    time = fields.Integer(string="First Unit")

    time_increment = fields.Integer(string="First Unit")

    dim1 = fields.Float(string='Product Dim1', digits=dp.get_precision(
        'Shipping Estimator'), help="can be length, width, height, depth, diameter, but 3 orthogonal Dims are required")    

    dim2 = fields.Float(
        string='Product Dim2', digits=dp.get_precision('Shipping Estimator'))

    dim3 = fields.Float(
        string='Product Dim3', digits=dp.get_precision('Shipping Estimator'))
    dim3_increment = fields.Float(
        string='Product Dim3 Increment', digits=dp.get_precision('Shipping Estimator'))

    cross_section = fields.Float(
        string='Product Section', digits=dp.get_precision('Shipping Estimator'))

    nmfc_code = fields.Many2one('nmfc.class', string='NMFC Code')
    nmfc_class = fields.Char(related='nmfc_code.nmfc_class', string='NMFC Class')
    nmfc_desc = fields.Char(related='nmfc_code.description', string='NMFC Description')

    description_picking = fields.Text('Description on Picking', translate=True)

    picking_warn_msg = fields.Text("Picking Warning Message")

    packing_warn_msg = fields.Text("Packing Warning message")

    shipping_comment = fields.Text("Picking Line Note")

    # purchase

    markup = fields.Float(string='Markup')
    purchase_line_warn_msg = fields.Text('Message for Purchase Order Line')
    purchase_receving_warn_msg = fields.Text('Receiving Warning')
    purchase_inspect_warn_msg = fields.Text('Inspection Warning')
    purchase_restock_warn_msg = fields.Text('Restocking Warning')
    purchase_comment = fields.Text('Purchasing Comments')

    # accounting
    account_comment = fields.Text('Accounting Comments')
    accounting_warn_msg = fields.Text('Accounting Warning')
    accounting_comment = fields.Text('Accounting Comments')

    vendor_count = fields.Integer(string='Vendors', compute='product_supplier_info_count')
    project_count = fields.Integer(string='Projects')
    task_count = fields.Integer(string='Tasks')
    document_count = fields.Integer(string='Documents',compute='action_document_count')
    website = fields.Integer(string='Websites')
    inventory_count = fields.Integer(string='Inventory')
    transfer_count = fields.Integer(string='Transfer')


    @api.multi
    def product_supplier_info_count(self):
        for rec in self:
            vendor_product_id = self.env['product.supplierinfo'].search([('product_id','=',rec.id)])
            rec.vendor_count = len(vendor_product_id)

    product_surcharge_purchase = fields.Float(
        string='Product Surcharge', help="Charge assessed once for each product unit")

    @api.multi
    def write(self,vals): 
        res = super(ProductProduct, self).write(vals)
        non_template_field = {}
        # if vals.get('name'):
        #     self.product_tmpl_id.write({'name':self.name})
        # sale part
        # if vals.get('categ_id')  and not self._context.get('sale_multi_pricelist_product_template'):
        #     non_template_field.update({'categ_id':False})
        if vals.get('lst_price')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'lst_price':0.0})

        if vals.get('sale_delay')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'sale_delay':0.0})
            
        if vals.get('produce_delay')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'produce_delay':0.0})

        if vals.get('public_categ_ids')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'public_categ_ids':False})

        if vals.get('optional_product_ids')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'optional_product_ids':False})

        if vals.get('alternative_product_ids')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'alternative_product_ids':False})

        if vals.get('accessory_product_ids')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'accessory_product_ids':False})                 

        if vals.get('available_in_pos')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'available_in_pos':False})
        if vals.get('to_weight')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'to_weight':False})
            
        if vals.get('pos_categ_id')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'pos_categ_id':False})


        if vals.get('description_quote')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'description_quote':False})
            
        if vals.get('description_sale')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'description_sale':False})

        if vals.get('sale_line_warn_msg')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'sale_line_warn_msg':False})          
        
        if vals.get('description')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'description':False})

        # inventory
        if vals.get('tracking')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'tracking':'none'}) 

        if vals.get('sale_ok')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'sale_ok':False})    
        
        if vals.get('purchase_ok')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'purchase_ok':False})

        if vals.get('can_be_expensed')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'can_be_expensed':False})

        if vals.get('recurring_invoice')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'recurring_invoice':False})
            
        if vals.get('life_time')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'life_time':0})

        if vals.get('use_time')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'use_time':0})

        if vals.get('removal_time')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'removal_time':0})

        if vals.get('alert_time')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'alert_time':0})

        if vals.get('route_ids')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'route_ids':False})    

        if vals.get('hs_code')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'hs_code':False})         
        
        if vals.get('description_pickingout')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'description_pickingout':False})
        
        # shipping
        if vals.get('picking_warn_msg')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'picking_warn_msg':False})

        if vals.get('description_picking')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'description_picking':False})    
            
        if vals.get('nmfc_code')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'nmfc_code':False})

        if vals.get('packing_warn_msg')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'packing_warn_msg':False})            
        
        if vals.get('shipping_comment')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'shipping_comment':False})
        
        # Purchasing
        if vals.get('markup')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'markup':False})
            
        if vals.get('purchase_line_warn_msg')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'purchase_line_warn_msg':False})

        if vals.get('purchase_receving_warn_msg')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'purchase_receving_warn_msg':False})          
        
        if vals.get('purchase_inspect_warn_msg')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'purchase_inspect_warn_msg':False})
        if vals.get('purchase_restock_warn_msg')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'purchase_restock_warn_msg':False})
        if vals.get('purchase_comment')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'purchase_comment':False})    

        # accounting
        if vals.get('account_comment')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'account_comment':False})
        if vals.get('accounting_warn_msg')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'accounting_warn_msg':False})
        if vals.get('accounting_comment')  and not self._context.get('sale_multi_pricelist_product_template'):
            non_template_field.update({'accounting_comment':False})
        if non_template_field:    
            self.product_tmpl_id.with_context(set_price_zero=True).write(non_template_field)
        return res

    def action_project_count_temp(self):
        return True

    def action_inventory_count_temp(self):
        return True

    def get_product_tasks(self):
        return True

    def action_transfer_count_temp(self):
        return True

    def action_document_count(self):
        for rec in self:
            rec.document_count=len(rec.product_documents_ids.ids)
        return True

    
    @api.multi
    def get_document_view(self):
        wizard_form = self.env.ref('product_extension.product_document_list').read()[0]
        wizard_form['domain'] = [ ('product_id', 'in', self.ids)]
        return wizard_form
        

    def action_website_temp(self):
        return True

    @api.multi
    def approve_product(self):
        for rec in self:
            rec.write({'status':'private'})

    #publish button
    @api.multi
    def publish_action(self):
        self.unpublish_product = False
        self.product_tmpl_id.write({'status':'public'})
        self.product_tmpl_id.website_published = True
        for rec in self:
            rec.write({'status':'public'})

    #unpublish button
    @api.multi
    def unpublish_action(self):
        self.unpublish_product = True
        for rec in self:
            rec.write({'status':'private'})

    #inactive button
    @api.multi
    def deactivate_action(self):
        self.unpublish_product = True
        self.active = False
        for rec in self:
            rec.write({'status':'inactive'})


    # activate button
    @api.multi
    def activate_action(self):
        self.unpublish_product = True
        self.active = True
        for rec in self:
            rec.write({'status':'private'})



class ProductAttributecustom(models.Model):
    _inherit = "product.attribute"

    # YTI FIX ME: PLEASE RENAME ME INTO attribute_type
    type = fields.Selection([
            ('select', 'Select'),
            ], default='select', required=True)
