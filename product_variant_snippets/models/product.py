# -*- coding: utf-8 -*-
from odoo import fields, models,api


class ProductTemplate(models.Model):

    _inherit = "product.template"

    currency_symbol = fields.Char(related="currency_id.symbol", string='Currency Symbol')

    @api.model
    def get_posible_combi(self,product_template_id,attribute_value_id,attribute_id):
        product_template_id=self.env['product.template'].search([('id','=',product_template_id)])
        attribute_ids=product_template_id._get_valid_product_template_attribute_lines();
        product_variant_ids=self.env['product.product'].search([('id','in',product_template_id.product_variant_ids.ids),('unpublish_product','!=',True)])
        final_temp_lis=[]
        final_dict={}
        temp_list=[]
        for rec in product_variant_ids:
            for attribute in rec.attribute_value_ids:
                if attribute.id not in temp_list:
                    temp_list.append(attribute.id)
        for rec in attribute_ids:
            temp=[]
            final_temp_lis=[]
            if int(attribute_id) != rec.attribute_id.id:
                for attribute in rec.product_template_value_ids:
                    if attribute.product_attribute_value_id.id in temp_list:
                        if rec.uom_ids:
                            final_temp_lis.append([attribute.id,attribute.name,rec.uom_ids.name])
                        else:
                            final_temp_lis.append([attribute.id,attribute.name,''])
                final_dict[rec.attribute_id.id]=final_temp_lis
        return {'product_template_id': product_template_id.id,
                    'final_dict':final_dict,}


class Product(models.Model):

    _inherit = "product.product"

    currency_symbol = fields.Char(related="currency_id.symbol", string='Currency Symbol')





    @api.model
    def search_product_variants(self,product_template_id):
    	if(type(product_template_id) == int ):
    		product_id = self.env['product.product'].sudo().search([('product_tmpl_id','=',product_template_id),('status','=','public')])
    	
    	else:
    		product_id = self.env['product.product'].sudo().search([('product_tmpl_id','=',product_template_id['id']),('status','=','public')])
    	
    	temp_data=[]
    	data={}
    	for rec in product_id:
    		temp_data=[]
    		temp_data.append(rec.id)
    		temp_data.append(rec.full_name)
    		data[rec.id]=temp_data
    	


    	return data
