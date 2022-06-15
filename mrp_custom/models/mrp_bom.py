# -*- coding: utf-8 -*-
# Copyright 2018 Akili
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class MrpBom(models.Model):
    _inherit = 'mrp.bom'


    @api.depends('product_id', 'product_tmpl_id')
    def get_bom_name(self):
        if self.product_id : 
            self.name = self.product_id.full_name
        elif self.product_tmpl_id:
            self.name = self.product_tmpl_id.name

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_mrp_bom_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_mrp_bom_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    # from sale_selection_kit module start
    _order = 'sequence'
    sequence = fields.Integer(string='sequence', help="Gives the sequence order when displaying a list of product categories.")
    name = fields.Char(string="Bom Name", compute="get_bom_name", store=True)
    type = fields.Selection([
        ('normal', 'Assembly'),
        ('phantom', 'Kit'),
        ('set', 'Set'),
        ('bundle', 'Bundle')], 'BOM Type',
        default='normal', required=True,
        help="Kit (Phantom): When processing a sales order for this product, the delivery order will contain the raw materials, instead of the finished product.")

    state = fields.Selection(
        [('draft', 'Draft'),
         ('active', 'Active'),
         ('inactive', 'Inactive'),
        ], required=True, default='draft')

    
    set_default = fields.Boolean("Set as Default")
    readonly_default = fields.Boolean("Set readonly")
    from_temp = fields.Boolean(compute="_from_temp")
    from_product = fields.Boolean(compute="_from_product")
    have_product = fields.Boolean(compute="_have_product")
    have_temp_product = fields.Boolean(compute="_have_temp_product")
    max_quantity  = fields.Integer("Max. Quantity")
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',required=False,
        domain="[('product_type', 'in', ['product', 'consu'])]")

    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        domain="[('product_type', 'in', ['product', 'consu'])]",
        help="If a product variant is defined the BOM is available only for this product.")
    product_id_as_per_redirect = fields.Many2one('product.product', compute="_compute_product_id_as_per_redirect")

    # from sale_selection_kit module end

    # from so_do_workflow module start
    read_only = fields.Boolean(compute="_compute_read_only")
    bom_line_ids_compute = fields.One2many('mrp.bom.line', 'bom_id_compute', 'BoM Lines',store=False, compute="_compute_bom_line_ids_compute")
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of bills of material.")

    
    bom_line_component_ids = fields.One2many('mrp.bundle.line', 'bom_bundle_component_id')
    temp_quantity_equal    = fields.Boolean()




    @api.one
    def _compute_bom_line_ids_compute(self):

        def common_data(list1, list2): 
            result = False
            for x in list1: 
                for y in list2: 
                    if x == y: 
                        result = True
                        return result  
            return result

        if self.env.context.get('default_from_product'):
            related_recordset = self.env["mrp.bom.line"].search([('bom_id','=',self.id)])
            product_id = self.env.context.get('default_product_id')
            product_rec = self.env['product.product'].browse(product_id)
            product_attribute_ids = product_rec.attribute_value_ids.ids
    
            vals = []
            for bom_line in related_recordset:
                if not bom_line.attribute_value_ids:
                    vals.append(bom_line.id)
                else:
                    bom_product_attribute_ids = bom_line.attribute_value_ids.ids
                    if common_data(product_attribute_ids, bom_product_attribute_ids):
                        vals.append(bom_line.id)

            self.bom_line_ids_compute = self.env["mrp.bom.line"].browse(vals)


    @api.multi
    def _compute_read_only(self):
        for each in self:
            if self.env.context.get('default_from_product') and self.product_id:
                each.read_only = False
            elif self.env.context.get('default_from_temp') and not self.product_id:
                each.read_only = False
            else:
                each.read_only = True      
    # from so_do_workflow module end    

    # from sale_selection_kit module start

    @api.multi
    def _compute_product_id_as_per_redirect(self):
        if self.env.context.get('default_from_product'):
            product_id = self.env.context.get('default_product_id')
            product_rec = self.env['product.product'].browse(product_id)
            for each in self:
                each.product_id_as_per_redirect = product_rec


    @api.multi
    def _from_product(self):
        if self._context.get('default_from_product'):
            for each in self:
                each.from_product =  True

    @api.multi
    def _have_product(self):
        for each in self:
            each.have_product = True if each.product_id else False

    @api.multi
    def _have_temp_product(self):
        for each in self:
            each.have_temp_product = True if each.product_tmpl_id else False        

    @api.multi
    def _from_temp(self):
        if self._context.get('default_from_temp'):
            for each in self:
                each.from_temp =  True

    @api.onchange('product_tmpl_id', 'type', 'product_id')
    def onchange_product_tmpl_id_check(self):
        if self.product_id:
            if self.product_id.product_type == 'set':
                self.type = 'set'
        if self.product_tmpl_id:
            if self.product_tmpl_id.product_type == 'set':
                self.type = 'set'
        if self.type:
            if self.type != 'set' and (self.product_tmpl_id.product_type == 'set' or self.product_id.product_type == 'set'):
                self.type = 'set'
                raise UserError(_("Default Product Type set !!!"))   
             

    @api.multi
    def name_get(self):
        res = [] 
        for bom in self:
            if bom.product_id:
                res.append((bom.id, bom.product_id.full_name)) 
                return res
            else:
                return super(MrpBom, self).name_get()
 
    @api.onchange('set_default')
    def onchange_default(self):
        if self.set_default:
            self.readonly_default = True 

    @api.onchange('max_quantity')
    def onchange_default_max_quantity(self):
        temp=0
        for rec in self.bom_line_component_ids:
            temp=temp+rec.minimum_product
        if  temp == self.max_quantity:
            self.temp_quantity_equal=True
        else:
            self.temp_quantity_equal=False

        if temp > self.max_quantity:
            self.max_quantity=temp
            raise UserError(_("Please enter amount above "+str(temp)+ " in maximium quantity")) 



    @api.onchange('bom_line_component_ids')
    def onchange_default_bom_line_ids(self):
        temp=0
        for rec in self.bom_line_component_ids:
            temp=temp+rec.minimum_product
        self.max_quantity=temp

    @api.model
    def create(self, vals):
        if 'readonly_default' in vals:                
            vals['set_default'] = vals['readonly_default']
        if vals['set_default'] == True:
            bom = self.search([('product_tmpl_id','=',vals.get('product_tmpl_id')),
                               ('set_default','=',True),('type','=', 'set')])       
            if bom:
                raise UserError(_("Default BOM Already Exists for this Product"))   
        if vals['set_default'] == False:
            bom = self.search([('product_tmpl_id','=',vals.get('product_tmpl_id')),
                               ('set_default','=',True),('type','=', 'set')])        
            if not bom:
                vals['set_default'] = True   
        res = super(MrpBom, self).create(vals) 
        product_id = self.env['product.product'].search([('id', '=', vals.get('product_tmpl_id'))])
        if product_id: 
            product_id.write({'kit':True, 'sale_ok':False, 'purchase_ok':False, 'can_be_expensed': False})
        return res

    @api.multi
    def write(self, vals): 
        bom = False
        for rec in self:
            if 'readonly_default' in vals:                
                vals['set_default'] = vals['readonly_default']
            if 'set_default' in vals:
                if vals['set_default'] == True: 
                    bom = self.search([('product_tmpl_id','=',rec.product_tmpl_id.id),
                                   ('set_default','=',True),('type','=', 'set')]) 
                    if bom: 
                       bom.write({'set_default':False, 'readonly_default':False})
        res = super(MrpBom, self).write(vals) 
        return res

    def set_state_active(self):
        if self.type == 'bundle':
            bom_ids = self.env['mrp.bom'].search([('type','=','bundle'),('product_id.id','=',self.product_id.id),('id' ,'!=',self.id),('state','=','active')])
            for rec in bom_ids:
                rec.state='draft'
        self.state='active'
        return True
    def reset_to_draft(self):
        self.state='draft'
        return True
    def set_to_inactive(self):
        self.state='inactive'
        return True


# from sale_selection_kit module end

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    bom_id_compute = fields.Many2one('mrp.bom', 'Parent BoM')

class MrpBundleLine(models.Model):
    _name = 'mrp.bundle.line'
    _description = 'Mrp Bundle Lines'
    
    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')

    select_product_temp = fields.Many2one('product.template', string='Bundle Selector')
    select_product_variant = fields.Many2one('product.product', string='Bundle Selection')
    minimum_product = fields.Integer(string='Minimum')
    maximum_product = fields.Integer(string='Maximum')
    product_source = fields.Char(string='Source')
    product_description = fields.Char(string='Description')

    bom_bundle_component_id = fields.Many2one('mrp.bom')

    product_bom_templ_ids = fields.One2many("product.template",'templ_bom_line_id',"Product Template")
    product_bom_var_ids = fields.One2many("product.product",'var_bom_line_id',"Product variant")

    # def variant_id(self):
    #     var_id = self.env["product.product"].search90
