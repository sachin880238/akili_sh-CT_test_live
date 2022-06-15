# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp
import logging
from odoo import tools
import base64

from PIL import Image
import requests
from io import BytesIO
import urllib
import io

import urllib.request


from PIL import ImageDraw
from PIL import ImageFont
import os
import logging
import tempfile


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    # image_medium = fields.Binary(
    #     "Image", compute='_compute_main_images',
    #     help="This field holds the image used as image for the product, limited to 1024x1024px.")


    # image = fields.Binary(
    #     "Image", compute='_compute_main_images',
    #     help="This field holds the image used as image for the product, limited to 1024x1024px.")

    # @api.depends('product_image_ids.main')
    # def _compute_main_images(self):
    #     for rec in self:
    #         rec.image_medium = rec.get_main_images().image
    #         rec.image = rec.get_main_images().image

    product_image_ids = fields.One2many('product.image', 'product_tmpl_id', string='Images')
    main_change = fields.Boolean("main_change")
    line_change = fields.Boolean("line change")

    @api.onchange('image_medium')
    def _onchange_image_medium(self):
        # self.product_image_ids.image = self.image_medium
        #prod_img = self.env['product.image'].search([('main','=',True)])
        if not self.image_medium or self.main_change:
            self.main_change = False
            return False
        for image in self.product_image_ids:
            if image.main:
                image.main = False
        self.product_image_ids = [(0,0,{'main':True,'selector':True,'image':self.image_medium})]
                



    @api.multi
    def get_main_images(self):
        return self.env['product.image'].search([('main','=',True),('id','in',self.product_image_ids.ids)],limit=1)

    @api.multi
    def get_selector_images(self):
        return self.env['product.image'].search([('selector','=',True),('main','=',False),('id','in',self.product_image_ids.ids)])

    @api.multi
    def get_line_images(self):
        return self.env['product.image'].search([('line','=',True),('id','in',self.product_image_ids.ids)],limit=1)


    @api.model_create_multi
    def create(self, vals_list): 
        res = super(ProductTemplate, self).create(vals_list)
        product_image_env = self.env['product.image']
        if res.product_image_ids:
            for product in res.product_variant_ids:
                product_images_dict = {}
                for images_extra in res.product_image_ids:
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
        if res.product_documents_ids:
            for product in res.product_variant_ids: 
                product_images_dict = {}
                for product_document in res.product_documents_ids:
                    product_document_dict = {
                        'description': product_document.description,
                        'name': product_document.name,
                        'file_type': product_document.file_type,
                        'datas': product_document.datas and product_document.datas or False ,
                        'product_id': product.id,
                        'public': product_document.public,
                        'file_link': product_document.file_link,
                        'create_date': product_document.create_date,
                    }
                    product_document_env.create(product_document_dict)
        return res


    @api.multi
    def write(self,vals):
        old_images_ids = self.product_image_ids
        old_vaiant_ids = self.product_variant_ids
        old_document_ids = self.product_documents_ids

        res = super(ProductTemplate, self).write(vals)
        for rec in self:
            new_images_ids = rec.product_image_ids
            new_variant_ids = rec.product_variant_ids
            new_document_ids = rec.product_documents_ids
            product_image_env = rec.env['product.image']
            product_product_env = rec.env['product.product']
            product_document_env = rec.env['ir.attachment']
            if vals.get('attribute_line_ids'):
                if new_variant_ids - old_vaiant_ids:
                    if len(old_vaiant_ids) < len(new_variant_ids):
                        for product_variant in new_variant_ids - old_vaiant_ids:
                            product_images_dict = {} 
                            for images_extra in old_images_ids:
                                product_images_dict = {
                                'image': images_extra.image,
                                'name': images_extra.name,
                                'main': images_extra.main,
                                'selector': images_extra.selector,
                                'line': images_extra.line,
                                'desc': images_extra.desc,
                                'file_link': images_extra.file_link,
                                'product_variant_id': product_variant.id,
                                'parent_id': images_extra.id,
                                }
                                product_image_env.create(product_images_dict)
                            
                            for product_document in old_document_ids:
                                product_document_dict = {
                                'description': product_document.description,
                                'name': product_document.name,
                                'file_type': product_document.file_type,
                                'datas': product_document.datas and product_document.datas or False ,
                                'product_id': product_variant.id,
                                'public': product_document.public,
                                'create_date': product_document.create_date,
                                }
                                product_document_env.create(product_document_dict)  
        
            if  vals.get('product_image_ids'): 
                temp = new_images_ids - old_images_ids
                if new_images_ids - old_images_ids:
                    if len(old_images_ids) < len(new_images_ids):
                        for product_variant in new_variant_ids:
                            for images_extra in new_images_ids - old_images_ids:
                                product_images_dict = {
                                    'image': False,
                                    'name': images_extra.name,
                                    'main': images_extra.main,
                                    'selector': images_extra.selector,
                                    'line': images_extra.line,
                                    'desc': images_extra.desc,
                                    'product_variant_id': product_variant.id,
                                    'file_link': images_extra.file_link,
                                    'parent_id': images_extra.id,
                                    'is_product_template': True,
                                }

                                # product_variant.write({'product_image_ids': [(6,0,  images_extra.ids)]})
                                # print("=======================================",product_variant.product_image_ids)

                                product_image_env.create(product_images_dict)

            
            if vals.get('product_documents_ids'):
                if new_document_ids - old_document_ids:
                    if len(old_document_ids) < len(new_document_ids):
                        for product_variant in new_variant_ids:
                            for product_document in new_document_ids - old_document_ids:
                                product_document_dict = {
                                'description': product_document.description,
                                'name': product_document.name,
                                'file_type': product_document.file_type,
                                'datas': product_document.datas and product_document.datas or False ,
                                'product_id': product_variant.id,
                                'public': product_document.public,
                                'create_date': product_document.create_date,
                                }
                                product_document_env.create(product_document_dict)

                # for product_variant in rec.product_variant_ids:
                #     if product_variant.product_documents_ids: 
                #         product_variant.product_documents_ids.unlink()
                #     for product_document in rec.product_documents_ids:
                #         product_document_dict = {
                #             'document_description': product_document.document_description,
                #             'document': product_document.document,
                #             'file_type': product_document.file_type,
                #             'product_document': product_document.product_document and product_document.product_document.id or False ,
                #             'product_id': product_variant.id,
                #             'is_publish': product_document.is_publish,
                #             # 'file_link': product_document.file_link,
                #             'date': product_document.date,
                #         }
                #         product_document_env.create(product_document_dict) 
        return res



    @api.onchange('product_image_ids')
    def _onchange_product_image_ids(self):
        count = 0
        update_main = False
        update_line = False
        main_image = False
        image_parent_id = 0
        for img in self.product_image_ids:
            if img.main_change:
                update_main = True
                break
            if img.main:
                main_image = True
                image_parent_id = img.id

        for img in self.product_image_ids:
            if img.line_change:
                update_line = True
                break
        if update_main:
            for img in self.product_image_ids:
                if img.main and img.main_change:
                    img.main_change = False 
                    self.main_change = True
                    self.image_medium = img.image 
                else:
                   img.main = False

        if update_line:
            for img in self.product_image_ids:
                if img.line and img.line_change:
                    img.line_change = False
                    self.line_change = True
                else:  
                    img.line = False

        if main_image:
            for variant in self.product_variant_ids:
                for img in variant.product_image_ids:
                    if img.id == image_parent_id:
                        img.main = True
                    else:
                        img.main = False
        for img in self.product_image_ids:
            if img.main == True:
                count+=1
                break
        if count == 0:
            self.image_medium = False
 
class ProductProduct(models.Model):
    _inherit = "product.product"


    # image_variant = fields.Binary(
    #     "Variant Image", compute='_compute_main_images',
    #     help="This field holds the image used as image for the product variant, limited to 1024x1024px.")

    product_image_ids = fields.One2many('product.image', 'product_variant_id', string='Images')
    main_change = fields.Boolean("main_change")


    temp_default = fields.Boolean(string='TDefault')
    

    @api.onchange('source_ids')
    def _source_ids(self):
        update_default = False
        for data in self.source_ids:
            if data.temp_default:
                update_default = True
                break

        if update_default:
            for data in self.source_ids:
                if data.default and data.temp_default:
                    data.temp_default = False 
                    self.temp_default = True
                else:
                   data.default = False

    # @api.depends('product_image_ids.main')
    # def _compute_main_images(self):
    #     for rec in self:
    #         rec.image_variant = rec.get_main_images().image

    @api.onchange('image_medium')
    def _onchange_image_medium(self):
        if not self.image_medium or self.main_change:
            self.main_change = False
            return False
        for image in self.product_image_ids:
            if image.main:
                image.main = False
        self.product_image_ids = [(0,0,{'main':True,'selector':True,'image':self.image_medium})]

    @api.multi
    def get_main_images(self):
        return self.env['product.image'].search([('main','=',True),('id','in',self.product_image_ids.ids)],limit=1)

    @api.multi
    def get_selector_images(self):
        return self.env['product.image'].search([('selector','=',True),('main','=',False),('id','in',self.product_image_ids.ids)])

    @api.multi
    def get_line_images(self):
        return self.env['product.image'].search([('line','=',True),('id','in',self.product_image_ids.ids)],limit=1)

    @api.onchange('product_image_ids')
    def _product_image_ids(self):
        count = 0
        update_main = False
        update_line = False
        for img in self.product_image_ids:
            if img.main_change:
                update_main = True
                break

        for img in self.product_image_ids:
            if img.line_change:
                update_line = True
                break

        if update_main:
            for img in self.product_image_ids:
                if img.main and img.main_change:
                    img.main_change = False 
                    self.main_change = True
                    self.image_medium = img.image 
                else:
                   img.main = False
        if update_line:
            for img in self.product_image_ids:
                if img.line and img.line_change:
                    img.line_change = False
                    self.line_change = True
                else:
                    img.line = False
        
        for img in self.product_image_ids:
            if img.main == True:
                count+=1
                break
        if count == 0:
            self.image_medium = False


class ProductImage(models.Model):
    _inherit = 'product.image'
    _order = 'sequence'

    @api.onchange('main','image')
    def _onchange_main(self):
        self.sequence_selected = True
        if self.main:
            self.main_change = True

    @api.onchange('line')
    def _change_line_image(self):
        if self.line:
            self.line_change = True
        else:
            self.line_change = False    

    @api.model
    def create(self,vals):
        date_list = []
        res = super(ProductImage, self).create(vals)
        if vals.get('main'):
            if res.product_variant_id:
                temp_image_ids = res.product_variant_id.product_image_ids
                for variant_image in temp_image_ids:
                    date_list.append(variant_image.create_date)
                for variant_image in temp_image_ids:
                    if variant_image.create_date != max(date_list):
                        variant_image.main = False
                res.product_variant_id.write({'image_variant':res.image}) 
            if res.product_tmpl_id:
                self.product_tmpl_id.write({'image':self.image})
        if vals.get('line'):
            if res.product_variant_id:
                temp_image_ids = res.product_variant_id.product_image_ids
                for variant_image in temp_image_ids:
                    date_list.append(variant_image.create_date)
                for variant_image in temp_image_ids:
                    if variant_image.create_date != max(date_list):
                        variant_image.line = False 
            if res.product_tmpl_id:
                temp_image_ids = res.product_tmpl_id.product_image_ids
                for template_image in temp_image_ids:
                    date_list.append(template_image.create_date)
                for template_image in temp_image_ids:
                    if template_image.create_date != max(date_list):
                        template_image.line = False
        return res

    @api.multi
    def unlink(self):
        for product_images in self:
            if product_images.is_product_template and product_images._context['params']['model']=='product.product':
                raise ValidationError(_('We can not unlink template record.'))
            if product_images.main:
                raise ValidationError(_('We can not unlink main record.')) 
            if 'sale_multi_pricelist_product_template' in product_images._context:
                for variant in product_images.product_tmpl_id.product_variant_ids:
                    for image in variant.product_image_ids:
                        if product_images.id == image.parent_id.id:
                            image.unlink()
            # product_images._context['params']['model']=='product.product'
            if product_images.parent_id and 'sale_multi_pricelist_product_template' not in product_images._context:
                raise ValidationError(_('We can not unlink record from Product.'))
        res = super(ProductImage, self).unlink()
        return res     
 
    parent_id = fields.Many2one('product.image', string='Parent Image')    
    product_tmpl_id = fields.Many2one('product.template', 'Related Product', copy=True) 
    product_variant_id = fields.Many2one('product.product', 'Related Product', copy=True)    
    image = fields.Binary('Image', attachment=True)
    # miduam_image = fields.Binary('Image',  compute='_compute_images' )
    main = fields.Boolean("Main")
    selector = fields.Boolean("Selector")
    line = fields.Boolean("Line")
    main_change = fields.Boolean("main_change")
    line_change = fields.Boolean("line_change")
    desc = fields.Text("Description")
    file_link = fields.Char("File/Link")
    sequence = fields.Integer(string='Sequence', default=10)
    sequence_selected = fields.Boolean(string='Sequence Selected')
    product_variant_image = fields.Binary(string='Image', compute='get_product_variant_image',store=False)
    virtual_image = fields.Binary(string='Image', compute='get_virtual_image',store=False)
    is_product_template = fields.Boolean(string='Is Template')


    def get_product_variant_image(self):
        for rec in self:
            if rec.parent_id:
                rec.product_variant_image = rec.parent_id.image

    def get_virtual_image(self):
        for rec in self:
            if rec.parent_id:
                rec.virtual_image = rec.parent_id.image
            else:
                 rec.virtual_image = rec.image

    @api.onchange('file_link')
    def get_file_link(self):
        img1 = False
        var_img = False
        try:
            if self.file_link:
                response = requests.get(self.file_link)
                img = Image.open(BytesIO(response.content))
                img.save('url_img.png')
                imgfile = Image.open('url_img.png')
                f = open('url_img.png' , 'rb') 
                img1 = base64.encodestring(f.read()) 
                f.close()
                os.remove('url_img.png')
                self.image = img1
        except:
            return {'warning': {
                            'title': _('Wrong url'),
                            'message': _('Please provide correct URL or check your image size.!')
                        }}        


    # @api.onchange('image')
    # def onchange_image(self):
    #     self.ensure_one()
    #     # if not self.image:
    #     #     raise UserError("no image on this record")
    #     # decode the base64 encoded data
    #     data = base64.decodestring(self.image)
    #     # create a temporary file, and save the image
    #     fobj = tempfile.NamedTemporaryFile(delete=False)
    #     fname = fobj.name
    #     fobj.write(data)
    #     fobj.close()
    #     self.file_link = fname
    #     # open the image with PIL
    #     try:
    #         image = Image.open(fname)
    #         # do stuff here
    #     finally:
    #         # delete the file when done
    #         os.unlink(fname)    
         

class ProductImageExtra(models.Model):
    _name = 'product.image.extra'
    _description = 'Product Image'

    name = fields.Char('Name')
    image = fields.Binary('Image', attachment=True)
