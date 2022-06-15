# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import itertools
from odoo import api, fields, models, _     , tools  
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp
import logging
from odoo.tools import pycompat
from openerp.tools import frozendict


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    status=fields.Selection([('draft','DRAFT'),('private','PRIVATE'),('public','PUBLIC'),('inactive','INACTIVE')], required="true",default="draft")
    sales_uom_ids = fields.Many2many('uom.uom', string='Sales Units')
    source_ids = fields.One2many('product.sources', 'product_tmpl_id', string='Source')
    hts_code = fields.Many2one('hts.description', string="HTS Code")
    hts_desc = fields.Char(related='hts_code.description', string="HTS Description")
    container_qty = fields.Integer(string="Container Quantity")
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    status_color = fields.Char(compute="get_product_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_product_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status_color = "#006400"
            elif rec.parent_state == "yellow":
                rec.status_color = "#FFD700"
            elif rec.parent_state == "red":
                rec.status_color = "#FF0000"
            else:
                rec.status_color = "#000000"

    @api.constrains('uom_id', 'sales_uom_ids')
    def _check_sales_uom(self):
        for template in self:
            for sales_uom in template.sales_uom_ids:
                if (template.uom_id and sales_uom and 
                    template.uom_id.category_id != sales_uom.category_id):
                    raise ValidationError(_('The Stock Unit of Measure and the Sales Unit of Measure must be in the same category.'))
        return True

    @api.multi
    def _get_selected_possible_combination(self,product_id):
        product_tmp_att_value_env = self.env['product.template.attribute.value']
        product_tmp_att_value = []
        product = self.env['product.product'].browse(int(product_id))
        if product:
            product_tmp_att_value = product_tmp_att_value_env.sudo().search([
                ('product_tmpl_id','=', product.product_tmpl_id.id),
                ('product_attribute_value_id','in',product.attribute_value_ids.ids)])
        if  product_tmp_att_value:
            return product_tmp_att_value

    @api.multi
    def view_active_and_inactive_variant(self):
        action = self.env.ref('product.product_normal_action_sell').read()[0]
        if self._context.get('active') and self.product_variant_ids:
            action['domain'] = [('id', 'in', self.product_variant_ids.ids)]
        if not self._context.get('active') and self.product_variant_ids:
            inactive_product = self.env['product.product'].search([('active','=',False),('product_tmpl_id','=',self.id)])    
            if inactive_product: 
                action['domain'] = [('id', 'in', inactive_product.ids)]
            else:
                return False
        if self.product_variant_ids:
            return action
        else:
            return False

    ## Product varient Tab Changes ##
    def _get_active_and_inactive_variants(self):
        for product in self:
            product.active_variants = len(product.product_variant_ids)
            product.inactive_variants = len(self.env['product.product'].search([('active','=',False),('product_tmpl_id','=',product.id)]))

    prod_attr_value = fields.Char('Attribute Value')
    master_product = fields.Char('Master Product', related='name')

    product_description = fields.Char(
            string='Product Description',
            required=False,
            readonly=False,
            index=False,
            default=None,
            help=False,
            translate=True
    )

    warranty = fields.Float('Warranty')    
    website_name = fields.Char("Website Title", compute='get_website_name', store=True, readonly=False)
    website_selection = fields.Selection(
        [('selection', 'Selection Dropdown'), ('attribute', 'Attribute Dropdown')], default='attribute', string="Website Selection")
    active_variants = fields.Char("Active Variants", compute='_get_active_and_inactive_variants')
    inactive_variants = fields.Char("Inactive Variants", compute='_get_active_and_inactive_variants')
    variant_image = fields.Binary("Variant-Image")
 
    @api.multi
    def name_get(self):
        result = []
        for pro in self:
            if pro.website_name:
                result.append((pro.id, pro.website_name))
            else:
                result.append((pro.id, pro.name))
        return result


    @api.depends('website_name')
    def get_website_name(self):
        for product in self:
            if product.compute_int:
                return True
            else :
                product.website_name = product.name
                product.compute_int = True

    compute_int = fields.Boolean(store=True)

    @api.onchange('website_name')
    def onchange_website_name(self):
        for product in self:
            if product.website_name:
                product.name = product.website_name
   
    @api.one
    def cal_cost(self):
        self.product_compute_quantity = self.standard_price * self.markup

    standard_price = fields.Float('Standard Price')
    defered_revenue = fields.Float('Deferred Revenue')
    accounting_type = fields.Char('Accounting Type')
    asset_category_id = fields.Char('Asset Category Id')

    @api.one
    def get_default_code(self):
        code = '' 
        if self.default_code:
            if self.default_code[0:1] != '[':
                code = '['+ str(self.default_code)
            else:
                code = self.default_code
            if self.default_code[len(self.default_code)-1:len(self.default_code)] != ']':
                code += '] '   
            self.product_code = code

    def get_template_attributes(self):
        for line in self:
            attr = []
            for attr_line in line.attribute_line_ids:
                attr.append(attr_line.attribute_id.id)
            if attr:  
                line.attr_list = attr
            else: 
                line.attr_list = False 


    def _get_default_category_id(self):
        if self._context.get('categ_id') or self._context.get('default_categ_id'):
            return self._context.get('categ_id') or self._context.get('default_categ_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        return category and category.id or False

    @api.depends('dim1','dim2','dim3')
    def _compute_volume(self):
        for rec in self:
            if rec.dim1 and rec.dim2:
                rec.volume = rec.dim1 * rec.dim2
            if rec.dim1 and rec.dim2 and rec.dim3:
                rec.volume = rec.dim1 * rec.dim2 * rec.dim3

    version = fields.Integer("Version")
    product_team_id = fields.Many2one('crm.team', string='Product Team', domain=[('sales_team', '=', True)])
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
    dedicated_container_id = fields.Many2one(
        'shipping.container', string='Product Container ID', help="Dedicated container for products that ship alone")
    container_quantity = fields.Integer(
        string='Product Container Quantity', help="alone product will fit into container above")
    cross_section = fields.Float(
        string='Product Section', digits=dp.get_precision('Shipping Estimator'))
    product_surcharge = fields.Float(
        string='Product Surcharge', help="Charge assessed once for each product unit")
    line_surcharge = fields.Float(
        string='Product Orderline Surcharge', help="Charge assessed once for each orderline")

    dim1 = fields.Float(string='Product Dim1', digits=dp.get_precision(
        'Shipping Estimator'), help="can be length, width, height, depth, diameter, but 3 orthogonal Dims are required")
    dim_uom_id = fields.Many2one('uom.uom', string="Dimension Unit")
    dim1_base = fields.Float(
        string='Product Dim1 Base', help="For nested or rollable products")
    dim1_increment = fields.Float(
        string='Product Dim1 Increment', help="For nested or rollable products")
    dim2 = fields.Float(
        string='Product Dim2', digits=dp.get_precision('Shipping Estimator'))
    dim2_base = fields.Float(string='Product Dim2 Base')
    dim2_increment = fields.Float(
        string='Product Dim2 Increment', digits=dp.get_precision('Shipping Estimator'))
    dim3 = fields.Float(
        string='Product Dim3', digits=dp.get_precision('Shipping Estimator'))
    dim3_base = fields.Float(string='Product Dim3 Base')
    dim3_increment = fields.Float(
        string='Product Dim3 Increment', digits=dp.get_precision('Shipping Estimator'))
    volume = fields.Float(string="Volume", compute='_compute_volume', readonly=False)
    nmfc_code = fields.Many2one('nmfc.class', string='NMFC Code')
    nmfc_desc = fields.Char(related='nmfc_code.description', string='NMFC Description')
    nmfc_class = fields.Char(related='nmfc_code.nmfc_class', string='NMFC Class')
    markup = fields.Float(string='Markup')
    comment = fields.Text(string='Comment')
    
    @api.depends('qty_available','virtual_available')
    def get_reserved_qty(self):
        if self._context.get('params'):
            if 'model' in self._context['params']:
                if self._context['params']['model'] == 'product.template':
                    if self.qty_available == self.virtual_available:
                        self.inventory_reserved = False
                    if self.qty_available > self.virtual_available:
                        self.inventory_reserved = self.qty_available - self.virtual_available

    # inventory Counting
    
    inventory_reserved = fields.Float('Current Reserved', help="Stock at reserved location", compute="get_reserved_qty")
    inventory_incoming = fields.Float('Incoming Inventory', help="Stock of incomming Shippment")
    incomming_reserved = fields.Float('Incoming Reserved', help="Stock Reserved from incomming Shippment")
    inventory_future = fields.Float('Future Available', help='Current Available + Incoming Inventory - Incoming Reserved')
  
    # end  inventory counting

    purc_order = fields.Float('Purchase Orders')
    purc_order = fields.Float('Purchase Orders')
    sales_per_day = fields.Float('Sales Per day')
    days_inventory = fields.Float('Days of Inventory')
    weight_increment = fields.Float('Weight Increment')
    note = fields.Text('Accounting Notes')
    description_inventory = fields.Text('Inventory Comments')
    inventory_comment = fields.Text('Inventory Comments')
    product_surcharge_purchase = fields.Float(
        string='Product Surcharge', help="Charge assessed once for each product unit")
    product_compute_quantity = fields.Float(compute=cal_cost, 
        string='Product Surcharge', help="Charge assessed once for each product unit")
    purchase_line_surcharge = fields.Float(
        string='Product Orderline Surcharge', help="Charge assessed once for each orderline")
    description_sale_note = fields.Text("Sales Notes") 
    sale_warn = fields.Selection(WARNING_MESSAGE, 'Sales Warning', default='no-message', help=WARNING_HELP, required=True )
    sale_line_warn_msg = fields.Text("Sales Warning")
    purchase_line_note = fields.Char("Purchase Line Note")
    can_be_expensed = fields.Boolean(help="Specify whether the product can be selected in an HR expense.", string="Can be Expensed")
    shipping_comment = fields.Text("Picking Line Note")
    picking_warn = fields.Selection(WARNING_MESSAGE, 'Picking Warning', help=WARNING_HELP, default='no-message', required=True)
    picking_warn_msg = fields.Text("Picking Warning Message")
    package_warn = fields.Selection(WARNING_MESSAGE, 'Packing Warning', help=WARNING_HELP, default='no-message', required=True)
    packing_warn_msg = fields.Text("Packing Warning message") 
    purchase_line_warn = fields.Selection(WARNING_MESSAGE, 'Purchase Order Line', help=WARNING_HELP, required=True, default="no-message")
    purchase_line_warn_msg = fields.Text('Message for Purchase Order Line')
    purchase_receving_warn_msg = fields.Text('Receiving Warning')
    purchase_comment = fields.Text('Purchasing Comments')
    purchase_inspect_warn_msg = fields.Text('Inspection Warning')
    purchase_restock_warn_msg = fields.Text('Restocking Warning')
    account_warn = fields.Text('Accounting Warning')
    account_comment = fields.Text('Accounting Comments')
    accounting_warn_msg = fields.Text('Accounting Warning')
    accounting_comment = fields.Text('Accounting Comments')
    product_code = fields.Char(compute=get_default_code, string="Product Code")
    suggested_sell = fields.Float('Suggested Sell', compute='_compute_price_calc')
    differential = fields.Float('Differential', compute='_compute_price_calc')
    sale_note = fields.Text(related='company_id.sale_note', string="Default Terms and Conditions *")
    recurring_invoice = fields.Boolean('Subscription Product', 
                               help='If set, confirming a sale order with this product will create a subscription')
    purchase_requisition = fields.Selection([('rfq', 'Create a draft purchase order'),('tenders', 'Propose a call for tenders')],
                                             string='Procurement', default='rfq')
    product_type = fields.Selection([('is_shipping', 'Shipping'),
                                    ('set', 'Set'),
                                    ('bundle', 'Bundle'), 
                                    ('consu', 'Consumable'),
                                    ('service', 'Service'),
                                    ('product', 'Merchandise'),
                                    ('container','Shipping Container')], string='Product Type', default='product')
    # optional_product_ids = fields.Many2many('product.product', 'product_optional_rel', 'src_id', 'dest_id',
    #                                         string='Optional Products', help="Optional Products are suggested "
    #                                         "whenever the customer hits *Add to Cart* (cross-sell strategy, "
    #                                         "e.g. for computers: warranty, software, etc.).")

    # alternative_product_ids = fields.Many2many('product.product', 'product_product_alternative_rel', 'src_id', 'dest_id',
    #                                            string='Alternative Products', help='Suggest alternatives to your customer'
    #                                            '(upsell strategy).Those product show up on the product page.')
    
    attr_list = fields.Many2many('product.attribute', compute='get_template_attributes', string='Attributes')
    description_quote = fields.Text("Sales Notes")
    download_count = fields.Integer("Downloads")
    image_medium = fields.Binary()
    time_uom = fields.Many2one("uom.uom", string="Time Unit")
    weight_time = fields.Integer(string="First Unit")
    weight_time_increment = fields.Integer(string="Each Additional")
    time = fields.Integer(string="First Unit")
    time_increment = fields.Integer(string="Each Additional")
    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id,
        required=True, help="Select category for the current product")
    list_price_selection_1 = fields.Selection([('lst_price_int', "")], string='A')
    list_price_selection_2 = fields.Selection([('lst_price_char', "")], string='B')
    vary_price = fields.Char("Vary Price")

    lst_price = fields.Float(
        'Public Price', digits=dp.get_precision('Product Price'))

    attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Attribute Values', ondelete='restrict')

    @api.model_create_multi
    def create(self, vals_list): 
        res = super(ProductTemplate, self).create(vals_list)    
        product_variant = {}

        # sale part
        if vals_list[0].get('name'):
            product_variant.update({'name':res.name})
        if vals_list[0].get('warranty'):
            product_variant.update({'warranty':res.warranty})        
        if vals_list[0].get('product_description'):    
            product_variant.update({'product_description':res.product_description})

        #if vals_list[0].get('categ_id'):
        #    product_variant.update({'categ_id':res.categ_id.id})

        if vals_list[0].get('lst_price'):
            product_variant.update({'lst_price':res.lst_price})    
        if vals_list[0].get('sale_delay'):
            product_variant.update({'sale_delay':res.sale_delay})

        if vals_list[0].get('product_team_id'):
            product_variant.update({'product_team_id':res.product_team_id.id})

        if vals_list[0].get('produce_delay'):
            product_variant.update({'produce_delay':res.produce_delay})
        
        if vals_list[0].get('public_categ_ids'):
            product_variant.update({'public_categ_ids':[(6, 0,res.public_categ_ids.ids)]})
        if vals_list[0].get('optional_product_ids'):
            product_variant.update({'optional_product_ids':[(6, 0,res.optional_product_ids.ids)]})
        if vals_list[0].get('alternative_product_ids'):
            product_variant.update({'alternative_product_ids':[(6, 0,res.alternative_product_ids.ids)]})
        if vals_list[0].get('accessory_product_ids'):
            product_variant.update({'accessory_product_ids':[(6, 0,res.accessory_product_ids.ids)]})
        
        if vals_list[0].get('available_in_pos'):
            product_variant.update({'available_in_pos':res.available_in_pos})
        if vals_list[0].get('to_weight'):
            product_variant.update({'to_weight':res.to_weight})
            
        if vals_list[0].get('pos_categ_id'):
            product_variant.update({'pos_categ_id':res.pos_categ_id.id})

        if vals_list[0].get('description_quote'):
            product_variant.update({'description_quote':res.description_quote})
        if vals_list[0].get('description_sale'):
            product_variant.update({'description_sale':res.description_sale})
        if vals_list[0].get('sale_line_warn_msg'):
            product_variant.update({'sale_line_warn_msg':res.sale_line_warn_msg})
        if vals_list[0].get('description'):
            product_variant.update({'description':res.description})

        # inventory
        if vals_list[0].get('tracking'):
            product_variant.update({'tracking':res.tracking}) 

        if vals_list[0].get('sale_ok'):
            product_variant.update({'sale_ok':res.sale_ok})    

        if vals_list[0].get('purchase_ok'):
            product_variant.update({'purchase_ok':res.purchase_ok})

        if vals_list[0].get('can_be_expensed'):
            product_variant.update({'can_be_expensed':res.can_be_expensed})

        if vals_list[0].get('recurring_invoice'):
            product_variant.update({'recurring_invoice':res.recurring_invoice})
            
        if vals_list[0].get('life_time'):
            product_variant.update({'life_time':res.life_time})

        if vals_list[0].get('use_time'):
            product_variant.update({'use_time':res.use_time})

        if vals_list[0].get('removal_time'):
            product_variant.update({'removal_time':res.removal_time})

        if vals_list[0].get('alert_time'):
            product_variant.update({'alert_time':res.alert_time})

        if vals_list[0].get('route_ids'):
            product_variant.update({'route_ids':[(6, 0, res.route_ids.ids)]}) 

        if vals_list[0].get('hs_code'):
            product_variant.update({'hs_code':res.hs_code})
        if vals_list[0].get('description_pickingout'):
            product_variant.update({'description_pickingout':res.description_pickingout})

        # shipping
        if vals_list[0].get('dim1'):
            product_variant.update({'dim1':res.dim1})

        if vals_list[0].get('dim2'):
            product_variant.update({'dim2':res.dim2})

        if vals_list[0].get('dim3'):
            product_variant.update({'dim3':res.dim3})

        if vals_list[0].get('dim3_increment'):
            product_variant.update({'dim3_increment':res.dim3_increment})

        if vals_list[0].get('cross_section'):
            product_variant.update({'cross_section':res.cross_section})

        if vals_list[0].get('description_picking'):
            product_variant.update({'description_picking':res.description_picking})
        
        if vals_list[0].get('nmfc_code'):
            product_variant.update({'nmfc_code':res.nmfc_code.id})

        if vals_list[0].get('picking_warn_msg'):
            product_variant.update({'picking_warn_msg':res.picking_warn_msg})

        if vals_list[0].get('packing_warn_msg'):
            product_variant.update({'packing_warn_msg':res.packing_warn_msg})          
        
        if vals_list[0].get('shipping_comment'):
            product_variant.update({'shipping_comment':res.shipping_comment})

        if vals_list[0].get('time'):
            product_variant.update({'time':res.time})

        if vals_list[0].get('time_increment'):
            product_variant.update({'time_increment':res.time_increment})    

        # Purchasing
        if vals_list[0].get('markup'):
            product_variant.update({'markup':res.markup})
            
        if vals_list[0].get('purchase_line_warn_msg'):
            product_variant.update({'purchase_line_warn_msg':res.purchase_line_warn_msg})

        if vals_list[0].get('purchase_receving_warn_msg'):
            product_variant.update({'purchase_receving_warn_msg':res.purchase_receving_warn_msg})           

        if vals_list[0].get('purchase_inspect_warn_msg'):
            product_variant.update({'purchase_inspect_warn_msg':res.purchase_inspect_warn_msg})
        if vals_list[0].get('purchase_restock_warn_msg'):
            product_variant.update({'purchase_restock_warn_msg':res.purchase_restock_warn_msg})
        if vals_list[0].get('purchase_comment'):
            product_variant.update({'purchase_comment':res.purchase_comment})   

        # accounting
        if vals_list[0].get('account_comment'):
            product_variant.update({'account_comment':res.account_comment})
        if vals_list[0].get('accounting_warn_msg'):
            product_variant.update({'accounting_warn_msg':res.accounting_warn_msg})
        if vals_list[0].get('accounting_comment'):
            product_variant.update({'accounting_comment':res.accounting_comment})    

        if product_variant:
            for product in res.product_variant_ids:
                product.write(product_variant)
        return res        


    @api.multi
    def write(self,vals):
        if 'active' in vals:
            if vals['active']:
                product_id = self.search([('name','=',self.name)]) 
                if product_id: 
                    raise UserError(_('Product with the same name already exists Kindly Archive that to Unarchive this'))
        if 'variant_image' in vals:
            if vals['variant_image']:
                variant_ids = self.env['product.product'].search([('product_tmpl_id','=',self.id)])
                for variant_id in variant_ids:
                    variant_id.write({'image_medium':vals['variant_image']})        
        res = super(ProductTemplate, self).write(vals)
        product_variant = {}

        #variants part
        if vals.get('product_description') and not self._context.get('set_price_zero'):    
            product_variant.update({'product_description':self.product_description})
        # sales part  
        #if vals.get('categ_id') and not self._context.get('set_price_zero'):
        #    product_variant.update({'categ_id':self.categ_id.id})
        if vals.get('warranty') and not self._context.get('set_price_zero'):
            product_variant.update({'warranty':self.warranty})
        if vals.get('lst_price') and not self._context.get('set_price_zero'):
            product_variant.update({'lst_price':self.lst_price})
        if vals.get('sale_delay') and not self._context.get('set_price_zero'):
            product_variant.update({'sale_delay':self.sale_delay})

        if vals.get('product_team_id') and not self._context.get('set_price_zero'):
            product_variant.update({'product_team_id':self.product_team_id.id})

        if vals.get('produce_delay') and not self._context.get('set_price_zero'):
            product_variant.update({'produce_delay':self.produce_delay})
        
        if vals.get('public_categ_ids') and not self._context.get('set_price_zero'):
            product_variant.update({'public_categ_ids':[(6, 0, self.public_categ_ids.ids)]})
        if vals.get('optional_product_ids') and not self._context.get('set_price_zero'):
            product_variant.update({'optional_product_ids':[(6, 0, self.optional_product_ids.ids)]})
        if vals.get('alternative_product_ids') and not self._context.get('set_price_zero'):
            product_variant.update({'alternative_product_ids':[(6, 0, self.alternative_product_ids.ids)]})
        # if vals.get('accessory_product_ids') and not self._context.get('set_price_zero'):
        #     product_variant.update({'accessory_product_ids' and not self._context.get('set_price_zero'):[(6, 0, self.accessory_product_ids.ids)]})       
        if vals.get('accessory_product_ids') and not self._context.get('set_price_zero'):
            product_variant.update({'accessory_product_ids':[(6, 0, self.accessory_product_ids.ids)]})       
        
        if vals.get('available_in_pos') and not self._context.get('set_price_zero'):
            product_variant.update({'available_in_pos':self.available_in_pos})
        if vals.get('to_weight') and not self._context.get('set_price_zero'):
            product_variant.update({'to_weight':self.to_weight})
        if vals.get('pos_categ_id') and not self._context.get('set_price_zero'):
            product_variant.update({'pos_categ_id':self.pos_categ_id.id})

        if vals.get('description_quote') and not self._context.get('set_price_zero'):
            product_variant.update({'description_quote':self.description_quote})
        if vals.get('description_sale') and not self._context.get('set_price_zero'):
            product_variant.update({'description_sale':self.description_sale})
        if vals.get('sale_line_warn_msg') and not self._context.get('set_price_zero'):
            product_variant.update({'sale_line_warn_msg':self.sale_line_warn_msg})
        if vals.get('description') and not self._context.get('set_price_zero'):
            product_variant.update({'description':self.description})

        # inventory 
        if vals.get('tracking') and not self._context.get('set_price_zero'):
            product_variant.update({'tracking':self.tracking}) 

        if vals.get('sale_ok') and not self._context.get('set_price_zero'):
            product_variant.update({'sale_ok':self.sale_ok})    

        if vals.get('purchase_ok') and not self._context.get('set_price_zero'):
            product_variant.update({'purchase_ok':self.purchase_ok})

        if vals.get('can_be_expensed') and not self._context.get('set_price_zero'):
            product_variant.update({'can_be_expensed':self.can_be_expensed})

        if vals.get('recurring_invoice') and not self._context.get('set_price_zero'):
            product_variant.update({'recurring_invoice':self.recurring_invoice})
            
        if vals.get('life_time') and not self._context.get('set_price_zero'):
            product_variant.update({'life_time':self.life_time})

        if vals.get('use_time') and not self._context.get('set_price_zero'):
            product_variant.update({'use_time':self.use_time})

        if vals.get('removal_time') and not self._context.get('set_price_zero'):
            product_variant.update({'removal_time':self.removal_time})

        if vals.get('alert_time') and not self._context.get('set_price_zero'):
            product_variant.update({'alert_time':self.alert_time})

        if vals.get('route_ids') and not self._context.get('set_price_zero'):
            product_variant.update({'route_ids':[(6, 0, self.route_ids.ids)]})     

        if vals.get('hs_code') and not self._context.get('set_price_zero'):
            product_variant.update({'hs_code':self.hs_code})
        if vals.get('description_pickingout')  and not self._context.get('set_price_zero'):
            product_variant.update({'description_pickingout':self.description_pickingout})
        
        # shipping
        if vals.get('packing_category') and not self._context.get('set_price_zero'):
            product_variant.update({'packing_category':self.packing_category})
        
        if vals.get('dedicated_container_id') and not self._context.get('set_price_zero'):
            product_variant.update({'dedicated_container_id': self.dedicated_container_id.id})
        
        if vals.get('container_quantity') and not self._context.get('set_price_zero'):
            product_variant.update({'container_quantity':self.container_quantity})
        
        if vals.get('product_surcharge') and not self._context.get('set_price_zero'):
            product_variant.update({'product_surcharge':self.product_surcharge})
        
        if vals.get('line_surcharge') and not self._context.get('set_price_zero'):
            product_variant.update({'line_surcharge':self.line_surcharge})
        
        if vals.get('dim1') and not self._context.get('set_price_zero'):
            product_variant.update({'dim1':self.dim1})

        if vals.get('dim2') and not self._context.get('set_price_zero'):
            product_variant.update({'dim2':self.dim2})

        if vals.get('dim3') and not self._context.get('set_price_zero'):
            product_variant.update({'dim3':self.dim3})

        if vals.get('dim3_increment') and not self._context.get('set_price_zero'):
            product_variant.update({'dim3_increment':self.dim3_increment})

        if vals.get('cross_section') and not self._context.get('set_price_zero'):
            product_variant.update({'cross_section':self.cross_section})

        if vals.get('description_picking') and not self._context.get('set_price_zero'):
            product_variant.update({'description_picking':self.description_picking})
        
        if vals.get('nmfc_code') and not self._context.get('set_price_zero'):
            product_variant.update({'nmfc_code':self.nmfc_code.id})

        if vals.get('picking_warn_msg') and not self._context.get('set_price_zero'):
            product_variant.update({'picking_warn_msg':self.picking_warn_msg})

        if vals.get('packing_warn_msg') and not self._context.get('set_price_zero'):
            product_variant.update({'packing_warn_msg':self.packing_warn_msg})          
        
        if vals.get('shipping_comment') and not self._context.get('set_price_zero'):
            product_variant.update({'shipping_comment':self.shipping_comment})

        if vals.get('time') and not self._context.get('set_price_zero'):
            product_variant.update({'time':self.time})

        if vals.get('time_increment') and not self._context.get('set_price_zero'):
            product_variant.update({'time_increment':self.time_increment})    
            
        # Purchasing
        if vals.get('markup') and not self._context.get('set_price_zero'):
            product_variant.update({'markup':self.markup})
            
        if vals.get('purchase_line_warn_msg') and not self._context.get('set_price_zero'):
            product_variant.update({'purchase_line_warn_msg':self.purchase_line_warn_msg})

        if vals.get('purchase_receving_warn_msg') and not self._context.get('set_price_zero'):
            product_variant.update({'purchase_receving_warn_msg':self.purchase_receving_warn_msg})          

        if vals.get('purchase_inspect_warn_msg') and not self._context.get('set_price_zero'):
            product_variant.update({'purchase_inspect_warn_msg':self.purchase_inspect_warn_msg})
        if vals.get('purchase_restock_warn_msg') and not self._context.get('set_price_zero'):
            product_variant.update({'purchase_restock_warn_msg':self.purchase_restock_warn_msg})
        if vals.get('purchase_comment') and not self._context.get('set_price_zero'):
            product_variant.update({'purchase_comment':self.purchase_comment})  

        # accounting
        if vals.get('account_comment') and not self._context.get('set_price_zero'):
            product_variant.update({'account_comment':self.account_comment})
        if vals.get('accounting_warn_msg') and not self._context.get('set_price_zero'):
            product_variant.update({'accounting_warn_msg':self.accounting_warn_msg})
        if vals.get('accounting_comment') and not self._context.get('set_price_zero'):
            product_variant.update({'accounting_comment':self.accounting_comment})
        if vals.get('name'):
            product_variant.update({'name':self.name})
        if product_variant:    
            for product in self.product_variant_ids:
                product.with_context(set_price_zero=True).write(product_variant)
        return res
    
    #addons function
    @api.multi
    def create_variant_ids(self,desire_values=[]):
        Product = self.env["product.product"]
        if "generate_variant" not in self._context:
            return False

        for tmpl_id in self.with_context(active_test=False):
            # Handle the variants for each template separately. This will be
            # less efficient when called on a lot of products with few variants
            # but it is better when there's a lot of variants on one template.
            variants_to_create = []
            variants_to_activate = self.env['product.product']
            variants_to_unlink = self.env['product.product']
            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            variant_alone = tmpl_id._get_valid_product_template_attribute_lines().filtered(lambda line: line.attribute_id.create_variant == 'always' and len(line.value_ids) == 1).mapped('value_ids')
            for value_id in variant_alone:
                updated_products = tmpl_id.product_variant_ids.filtered(lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
                updated_products.write({'attribute_value_ids': [(4, value_id.id)]})

            # Determine which product variants need to be created based on the attribute
            # configuration. If any attribute is set to generate variants dynamically, skip the
            # process.
            # Technical note: if there is no attribute, a variant is still created because
            # 'not any([])' and 'set([]) not in set([])' are True.
            if not tmpl_id.has_dynamic_attributes():
                # Iterator containing all possible `product.attribute.value` combination
                # The iterator is used to avoid MemoryError in case of a huge number of combination.
                all_variants = itertools.product(*(
                    line.value_ids.ids for line in tmpl_id.valid_product_template_attribute_line_wnva_ids
                ))
                # Set containing existing `product.attribute.value` combination
                existing_variants = {
                    frozenset(variant.attribute_value_ids.ids)
                    for variant in tmpl_id.product_variant_ids
                }
                # For each possible variant, create if it doesn't exist yet.
                for value_ids in all_variants:
                    exist_in_wizard = []
                    value_ids = frozenset(value_ids)
                    if value_ids not in existing_variants: 
                        for attr in value_ids:
                            attr_id = self.env['product.attribute.value'].search([('id','=',attr)])
                            if attr_id.name in desire_values:
                                exist_in_wizard.append(True)
                            else:
                                exist_in_wizard.append(False)
                        if all(exist_in_wizard):
                            variants_to_create.append({
                                'product_tmpl_id': tmpl_id.id,
                                'attribute_value_ids': [(6, 0, list(value_ids))],
                                'active': tmpl_id.active,
                            })
                            if len(variants_to_create) > 1000:
                                raise UserError(_(
                                    'The number of variants to generate is too high. '
                                    'You should either not generate variants for each combination or generate them on demand from the sales order. '
                                    'To do so, open the form view of attributes and change the mode of *Create Variants*.'))

            # Check existing variants if any needs to be activated or unlinked.
            # - if the product is not active and has valid attributes and attribute values, it
            #   should be activated
            # - if the product does not have valid attributes or attribute values, it should be
            #   deleted
            valid_value_ids = tmpl_id.valid_product_attribute_value_wnva_ids
            valid_attribute_ids = tmpl_id.valid_product_attribute_wnva_ids
            for product_id in tmpl_id.product_variant_ids:
                if product_id._has_valid_attributes(valid_attribute_ids, valid_value_ids):
                    if not product_id.active:
                        variants_to_activate += product_id
                else:
                    variants_to_unlink += product_id

            if variants_to_activate:
                variants_to_activate.write({'active': True})

            # create new products
            if variants_to_create:
                Product.create(variants_to_create)

            # unlink or inactive product
            # try in batch first because it is much faster
            try:
                with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                    variants_to_unlink.unlink()
            except Exception:
                # fall back to one by one if batch is not possible
                for variant in variants_to_unlink:
                    try:
                        with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                            variant.unlink()
                    # We catch all kind of exception to be sure that the operation doesn't fail.
                    except Exception:
                        # Note: this can still fail if something is preventing from archiving.
                        # This is the case from existing stock reordering rules.
                        variant.write({'active': False})

        # prefetched o2m have to be reloaded (because of active_test)
        # (eg. product.template: product_variant_ids)
        # We can't rely on existing invalidate_cache because of the savepoint.
        self.invalidate_cache()
        return True

    @api.onchange('purchase_line_warn_msg')
    def onchange_purchase_line_warn_msg(self):
        if self.purchase_line_warn_msg:
            self.purchase_line_warn = 'warning' 
        else :
            self.purchase_line_warn = 'no-message' 
        

    @api.onchange('picking_warn_msg')
    def onchange_picking_warn_msg(self):
        if self.picking_warn_msg:
            self.picking_warn = 'warning' 
        else :
            self.picking_warn = 'no-message' 
        
        
    @api.onchange('packing_warn_msg')
    def onchange_packing_warn_msg(self):
        if self.packing_warn_msg:
            self.package_warn = 'warning' 
        else :
            self.package_warn = 'no-message' 
        
        
    @api.onchange('sale_line_warn_msg')
    def onchange_sale_line_warn_msg(self):
        if self.sale_line_warn_msg:
            self.sale_warn = 'warning' 
        else :
            self.sale_warn = 'no-message' 
        
        

    @api.onchange('product_type')
    def onchange_lang(self):
        if self.product_type in ['is_shipping', 'service']:
            self.type = 'service'
        if self.product_type in ['consu', 'is_pallet', 'container']:
            self.type = 'consu'
        if self.product_type in ['product','set','bundle']:
            self.type = 'product'
        
        
    @api.multi
    @api.depends('markup', 'standard_price', 'list_price')
    def _compute_price_calc(self):
        for record in self:
            record.suggested_sell = record.standard_price * record.markup
            record.differential = record.suggested_sell - record.list_price

    #primary generate button
    @api.multi
    def generate_variants(self):
        wizard_form = self.env.ref('product_extension.generate_prod_variant_wizard_view', False)
        return {
                'name'      : _('Generate Variants'),
                'type'      : 'ir.actions.act_window',
                'res_model' : 'generate.prod.variant',
                'view_id'   : wizard_form.id,
                'view_type' : 'form',
                'view_mode' : 'form',
                'target'    : 'new'
            }
    
    #secondary generate button
    @api.multi
    def generate(self):
        wizard_form = self.env.ref('product_extension.generate_prod_variant_wizard_view', False)
        return {
                'name'      : _('Generate Variants'),
                'type'      : 'ir.actions.act_window',
                'res_model' : 'generate.prod.variant',
                'view_id'   : wizard_form.id,
                'view_type' : 'form',
                'view_mode' : 'form',
                'context'   : {'secondary' : True},
                'target'    : 'new'
            }

    #publish button
    @api.multi
    def publish_action(self):
        if self.website_published:
            for var in self.product_variant_ids:
                var.write({'status':'public'})
            for rec in self:
                rec.write({'status':'public'})
        product_id = self.env['product.product'].search([('product_tmpl_id','=',self.id),('status','=','public')])
        if not product_id :
            raise UserError(_('Atleast one variant should be published before publishing template.'))
        

    #unpulish button
    @api.multi
    def unpublish_action(self):
        # self.website_published = False
        for var in self.product_variant_ids:
            var.write({'status':'private'})
        for rec in self:
            rec.write({'status':'private'})

    #activate button
    @api.multi
    def activate_action(self):
        self.active = True
        product_env = self.env['product.product'].search([('website_name','=',self.website_name),('active','=',False)])
        for variant in product_env:
            variant.unpublish_product = True
            variant.active = True
            variant.write({'status':'private'})
        for rec in self:
            rec.write({'status':'private'})

    #inactive button
    @api.multi
    def deactivate_action(self):
        self.website_published = False
        product_env = self.env['product.product'].search([('website_name','=',self.website_name)])
        for variant in product_env:
            variant.unpublish_product = True
            variant.active = False
            variant.write({'status':'inactive'})
        self.active = False
        for rec in self:
            rec.write({'status':'inactive'})


    

    def update_products_variants(self):
        product_variant = {}
          
        #if vals.get('categ_id') and not self._context.get('set_price_zero'):
        #    product_variant.update({'categ_id':self.categ_id.id})

        #variants part
        product_variant.update({'product_description':self.product_description})

        # sales part
        product_variant.update({'warranty':self.warranty})
        product_variant.update({'lst_price':self.lst_price})
        product_variant.update({'sale_delay':self.sale_delay})
        product_variant.update({'product_team_id':self.product_team_id.id})
        product_variant.update({'produce_delay':self.produce_delay})
        product_variant.update({'public_categ_ids':[(6, 0, self.public_categ_ids.ids)]})
        product_variant.update({'optional_product_ids':[(6, 0, self.optional_product_ids.ids)]})
        product_variant.update({'alternative_product_ids':[(6, 0, self.alternative_product_ids.ids)]})
        # product_variant.update({'accessory_product_ids' and not self._context.get('set_price_zero'):[(6, 0, self.accessory_product_ids.ids)]})
        product_variant.update({'available_in_pos':self.available_in_pos})
        product_variant.update({'to_weight':self.to_weight})
        product_variant.update({'pos_categ_id':self.pos_categ_id.id})
        product_variant.update({'description_quote':self.description_quote})
        product_variant.update({'description_sale':self.description_sale})
        product_variant.update({'sale_line_warn_msg':self.sale_line_warn_msg})
        product_variant.update({'description':self.description})

        # inventory 
        product_variant.update({'tracking':self.tracking}) 
        product_variant.update({'sale_ok':self.sale_ok})    
        product_variant.update({'purchase_ok':self.purchase_ok})
        product_variant.update({'can_be_expensed':self.can_be_expensed})
        product_variant.update({'recurring_invoice':self.recurring_invoice})    
        product_variant.update({'life_time':self.life_time})
        product_variant.update({'use_time':self.use_time})
        product_variant.update({'removal_time':self.removal_time})
        product_variant.update({'alert_time':self.alert_time})
        product_variant.update({'route_ids':[(6, 0, self.route_ids.ids)]})     
        product_variant.update({'hs_code':self.hs_code})
        product_variant.update({'description_pickingout':self.description_pickingout})
        
        # shipping
        product_variant.update({'packing_category':self.packing_category})
        product_variant.update({'dedicated_container_id':self.dedicated_container_id.id})
        product_variant.update({'container_quantity':self.container_quantity})
        product_variant.update({'product_surcharge':self.product_surcharge})
        product_variant.update({'line_surcharge':self.line_surcharge})
        product_variant.update({'dim1':self.dim1})
        product_variant.update({'dim2':self.dim2})
        product_variant.update({'dim3':self.dim3})
        product_variant.update({'dim3_increment':self.dim3_increment})
        product_variant.update({'cross_section':self.cross_section})
        product_variant.update({'description_picking':self.description_picking})
        product_variant.update({'nmfc_code':self.nmfc_code.id})
        product_variant.update({'picking_warn_msg':self.picking_warn_msg})
        product_variant.update({'packing_warn_msg':self.packing_warn_msg})          
        product_variant.update({'shipping_comment':self.shipping_comment})
        product_variant.update({'time':self.time})
        product_variant.update({'time_increment':self.time_increment})

            
        # Purchasing
        product_variant.update({'markup':self.markup})    
        product_variant.update({'purchase_line_warn_msg':self.purchase_line_warn_msg})
        product_variant.update({'purchase_receving_warn_msg':self.purchase_receving_warn_msg})          
        product_variant.update({'purchase_inspect_warn_msg':self.purchase_inspect_warn_msg})
        product_variant.update({'purchase_restock_warn_msg':self.purchase_restock_warn_msg})
        product_variant.update({'purchase_comment':self.purchase_comment})  

        # accounting
        product_variant.update({'account_comment':self.account_comment})
        product_variant.update({'accounting_warn_msg':self.accounting_warn_msg})
        product_variant.update({'accounting_comment':self.accounting_comment})
        product_variant.update({'name':self.name})

        if product_variant:    
            for product in self.product_variant_ids:
                product.write(product_variant)
        return True

    def update_product_images(self):
        product_image_env = self.env['product.image']
        if self.product_image_ids:  
            for product in self.product_variant_ids: 
                product_images_dict = {}
                for images_extra in self.product_image_ids:
                    product_images_dict = {
                        'image': False,
                        'name': images_extra.name,
                        'main': images_extra.main,
                        'selector': images_extra.selector,
                        'line': images_extra.line,
                        'desc': images_extra.desc,
                        'file_link': images_extra.file_link,
                        'product_variant_id': product.id,
                        'parent_id': images_extra.id,
                        'is_product_template': True,
                    }
                    product_image_env.create(product_images_dict)
        product_document_env = self.env['ir.attachment']
        if self.product_documents_ids:
            for product in self.product_variant_ids: 
                product_images_dict = {}
                for product_document in self.product_documents_ids:
                    product_document_dict = {
                        'description': product_document.description,
                        'name': product_document.name,
                        'file_type': product_document.file_type,
                        'datas_fname':product_document.datas_fname,
                        'datas': product_document.datas and product_document.datas or False ,
                        'product_id': product.id,
                        'public': product_document.public,
                        # 'file_link': product_document.file_link,
                        'date': product_document.create_date,
                    }
                    product_document_env.create(product_document_dict)
            return True

    project_count = fields.Integer(string='Projects')
    task_count = fields.Integer(string='Tasks')
    document_count = fields.Integer(string='Documents',compute='action_document_count')
    website = fields.Integer(string='Websites')
    prod_values = fields.Integer(string='Values')
    inventory_count = fields.Integer(string='Inventory')
    transfer_count = fields.Integer(string='Transfer')
    vendor_count = fields.Integer(string='Vendors',compute='_compute_product_supplier_info_count')
    product_supplier_info_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id', 'Products')

    selection_vendor = fields.Selection([
        ('rfq', 'Create a draft purchase order'),
        ('tenders', 'Propose a call for tenders')],string='Procurement', default='rfq')
    primary_vendor = fields.Many2one('res.partner', string='Vendor Primary', compute='compute_primary_vendor')
    secondary_vendor = fields.Char('Vendor Secondary')
    vendor_stock_code = fields.Char(string='Vendor Stock ID', compute='compute_primary_vendor')
    vendor_description = fields.Text(string='Vendor Description', compute='compute_primary_vendor')
    price = fields.Float(string='Price')
    date_start = fields.Date(string='Price Effective',compute='compute_primary_vendor')
    date_end = fields.Date(string='Price Expires',compute='compute_primary_vendor')
    min_qty = fields.Integer(string='Minimum Quantity',compute='compute_primary_vendor')
    preferred = fields.Integer(string='Preferrd Quantity',compute='compute_primary_vendor')
    multiple = fields.Integer(string='Quantity Multiple',compute='compute_primary_vendor')
    delay = fields.Integer(string='Days to Ship',compute='compute_primary_vendor')


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

    @api.one
    @api.depends('product_supplier_info_ids.product_tmpl_id')
    def _compute_product_supplier_info_count(self):
        for rec in self:
            rec.vendor_count = len(rec.product_supplier_info_ids)

    def action_inventory_count_temp(self):
        return True

    def action_transfer_count_temp(self):
        return True

    @api.multi
    def action_website_temp(self):
        return True

    @api.multi
    def action_task_count_temp(self):
        return True

    def action_document_count(self):
        for rec in self:
            rec.document_count=len(rec.product_documents_ids.ids)  

    @api.multi
    def action_project_count_temp(self):
        return True

    @api.multi
    def action_values_count_temp(self):
        return True

    #.....Get Product Tree View
    @api.multi
    def get_variants_view(self):
        if self.product_variant_count > 0:
            action = self.env.ref('product_extension.product_variants_list').read()[0]
            return action
        else:
            return {
                    'name': _('Products'),
                    'view_type': 'form',
                    'view_mode': 'tree,form,kanban',
                    'res_model': 'product.product',
                    'domain':[('product_tmpl_id','=',self._context.get('active_id', False))],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    }
                    
    #.....Get Product variant Tree View
    @api.multi
    def get_template_variants_view(self):
        if self.product_variant_count > 0:
            action = self.env.ref('product_extension.template_variant_tree_view_action').read()[0]
            return action
        else:
            return {
                    'name': _('Products'),
                    'view_mode': 'tree',
                    'res_model': 'product.product',
                    'type': 'ir.actions.act_window',
                    'domain':[('product_tmpl_id','=',self._context.get('active_id', False))],
                    'view_id': self.env.ref('product_extension.template_variant_tree_view').id,
                    'target': 'current',
                    }

    @api.multi
    def get_document_view(self):
        wizard_form = self.env.ref('product_extension.product_document_list').read()[0]
        wizard_form['domain'] = [ ('product_tmp_id', 'in', self.ids)]
        return wizard_form

    # Override method
    @api.multi
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        """ Return info about a given combination.

        Note: this method does not take into account whether the combination is
        actually possible.

        :param combination: recordset of `product.template.attribute.value`

        :param product_id: id of a `product.product`. If no `combination`
            is set, the method will try to load the variant `product_id` if
            it exists instead of finding a variant based on the combination.

            If there is no combination, that means we definitely want a
            variant and not something that will have no_variant set.

        :param add_qty: float with the quantity for which to get the info,
            indeed some pricelist rules might depend on it.

        :param pricelist: `product.pricelist` the pricelist to use
            (can be none, eg. from SO if no partner and no pricelist selected)

        :param parent_combination: if no combination and no product_id are
            given, it will try to find the first possible combination, taking
            into account parent_combination (if set) for the exclusion rules.

        :param only_template: boolean, if set to True, get the info for the
            template only: ignore combination and don't try to find variant

        :return: dict with product/combination info:

            - product_id: the variant id matching the combination (if it exists)

            - product_template_id: the current template id

            - display_name: the name of the combination

            - price: the computed price of the combination, take the catalog
                price if no pricelist is given

            - list_price: the catalog price of the combination, but this is
                not the "real" list_price, it has price_extra included (so
                it's actually more closely related to `lst_price`), and it
                is converted to the pricelist currency (if given)

            - has_discounted_price: True if the pricelist discount policy says
                the price does not include the discount and there is actually a
                discount applied (price < list_price), else False
        """
        self.ensure_one()
        # get the name before the change of context to benefit from prefetch
        display_name = self.name

        quantity = self.env.context.get('quantity', add_qty)
        context = dict(self.env.context, quantity=quantity, pricelist=pricelist.id if pricelist else False)
        product_template = self.with_context(context)

        combination = combination or product_template.env['product.template.attribute.value']

        if not product_id and not combination and not only_template:
            combination = product_template._get_first_possible_combination(parent_combination)

        if only_template:
            product = product_template.env['product.product']
        elif product_id and not combination:
            product = product_template.env['product.product'].browse(product_id)
        elif all(combination.mapped('id')):
            product = product_template._get_variant_for_combination(combination)
        else:
            product = self.env['product.product']

        if product:
            # We need to add the price_extra for the attributes that are not
            # in the variant, typically those of type no_variant, but it is
            # possible that a no_variant attribute is still in a variant if
            # the type of the attribute has been changed after creation.
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in combination.filtered(
                    lambda ptav:
                        ptav.price_extra and
                        ptav not in product.product_template_attribute_value_ids
                )
            ]
            if no_variant_attributes_price_extra:
                product = product.with_context(
                    no_variant_attributes_price_extra=no_variant_attributes_price_extra
                )
            list_price = product.price_compute('list_price')[product.id]
            price = product.price if pricelist else list_price
        else:
            product_template = product_template.with_context(current_attributes_price_extra=[v.price_extra or 0.0 for v in combination])
            list_price = product_template.price_compute('list_price')[product_template.id]
            price = product_template.price if pricelist else list_price

        filtered_combination = combination._without_no_variant_attributes()
        if filtered_combination:
            if all(filtered_combination.mapped('name')):
                display_name = '%s (%s)' % (display_name, ', '.join(filtered_combination.mapped('name')))

        if pricelist and pricelist.currency_id != product_template.currency_id:
            list_price = product_template.currency_id._convert(
                list_price, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
                fields.Date.today()
            )

        price_without_discount = list_price if pricelist and pricelist.discount_policy == 'without_discount' else price
        has_discounted_price = (pricelist or product_template).currency_id.compare_amounts(price_without_discount, price) == 1

        return {
            'product_id': product.id,
            'product_template_id': product_template.id,
            'display_name': display_name,
            'price': price,
            'list_price': list_price,
            'has_discounted_price': has_discounted_price,
        }
