# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
import base64
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime
from odoo import fields
import json
import itertools

class ProductRedirect(WebsiteSale):


    @http.route(['/product/image_effect_config'], type='json', auth="public", website=True)
    def get_image_effect_config(self,product_template=None):
        products = False
        if product_template:
            products = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', product_template)])
        cur_website = request.website
        values = {
            'no_extra_options': cur_website.no_extra_options,
            'theme_panel_position': cur_website.thumbnail_panel_position,
            'interval_play': cur_website.interval_play,
            'enable_disable_text': cur_website.enable_disable_text,
            'color_opt_thumbnail': cur_website.color_opt_thumbnail,
            'change_thumbnail_size': cur_website.change_thumbnail_size,
            'thumb_height': cur_website.thumb_height,
            'thumb_width': cur_website.thumb_width,
            'products': products,
        }

        if products:
            values.update({'products':products.ids})
        return values


    @http.route(['/shop/product/<model("product.template"):product>',
        '/shop/product/<model("product.template"):product>/<model("product.product"):product_variant>/<model("mrp.bom"):bom>',
        '/shop/product/<model("product.template"):product>/<model("product.product"):cart_selected_product>'], type='http', auth="public", website=True)
    def product(self, product, product_variant=None,cart_selected_product=None, category='', search='', **kwargs):
        res = super(ProductRedirect, self).product(product=product, category=category, search=search, **kwargs)
        product_id = request.env['product.product'].search([])
        product_bom = request.env['mrp.bom'].search([])
        if res.qcontext.get('keep'):
            res.qcontext.get('keep').__dict__['path'] = '/find-a-product'
        if kwargs.get('variant-id'):
            selected_product = request.env['product.product'].browse(int(kwargs.get('variant-id')))
            res.qcontext.update({
                'selected_productimport itertools': selected_product,
                'selected_product_id': kwargs.get('variant-id'),
                
            })
        temp_final=[]
        for rec in product._get_valid_product_template_attribute_lines():
            temp=[]
            for value_ids in rec.product_template_value_ids:
                temp.append(value_ids.id)
            temp_final.append(temp)
        combinations_all = list(itertools.product(*temp_final))
        new_list=[]
        product_ids=[]
        for i in combinations_all:
            data= self.get_combination_info(product, product.product_variant_id, list(i),1, 1, **kwargs)
            if data['publish']==True:
                new_list.append(i)
                product_ids.append(data['product_id'])
        product_product_ids=request.env['product.product'].search([('id','in',product_ids)])
        temp_list=[]
        for rec in product_product_ids:
            for attribute in rec.attribute_value_ids:
                for value_ids in attribute:
                    if value_ids.id not in temp_list:
                        temp_list.append(value_ids.id)
        res.qcontext.update({
                
                'temp_list':temp_list,
                
            })



        # if kwargs.get('bom-id'):
        #     selected_product = request.env['product.product'].browse(int(kwargs.get('bom-id')))
        #     res.qcontext.update({
        #         'selected_product': selected_product,
        #         'selected_bom_id': kwargs.get('bom-id'),

        #     })      
        if product_variant:
            res.qcontext.update({
                'product_variant': product_variant,
                'selected_product_id': product_variant,
                'selected_product':product_variant,
                'selected_product_variant': True
            })
        if cart_selected_product:
            value_list=[]
            for value in cart_selected_product.product_template_attribute_value_ids:
                value_list.append(value.product_attribute_value_id.id)
            res.qcontext.update({
                'variant_found':True,
                'value_list':value_list,
                'cart_selected_product':cart_selected_product,
                'product_variant': cart_selected_product,
                'selected_product_id': cart_selected_product,
                'selected_product':cart_selected_product,
                'selected_product_variant': True
            })
        else:
            res.qcontext.update({
                'variant_found':False,
                })


        return res


    @http.route(['/website_product_detail_page/get_update_product_image'], type='json', auth="public", methods=['POST'], website=True)
    def get_update_product_image(self, product_template_id, product_id, **kw):
        res ={
            'product_id': product_id,
            'product_template_id': product_template_id
        }
        kw.pop('pricelist_id')
        if request.env.ref('website_product_detail_page.website_select_option', raise_if_not_found=False):  # IF for compatibility 12.0
            res.update(carousel=request.env['ir.ui.view'].render_template('website_product_detail_page.website_select_option', values={
                'product': request.env['product.template'].browse(res['product_template_id']),
                'product_variant': request.env['product.product'].browse(res['product_id']),
            }))
        return res    

    # @http.route(['/shop/find_product_template'], type='json', auth="public", website=True)
    # def find_product_template(self,product_id=None,**kwargs):
    #     product_templ = request.env['product.product'].sudo().browse(product_id)

    #     if product_templ:
    #         return {'product_templ': product_templ.id,
    #             'lst_price':product_templ.lst_price}

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, variant_quantity=None, variant_ids=None,
                         set_qty=None, display=True):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        

        order = request.website.sale_get_order(force_create=1)
       
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        if variant_ids != None:
            length = len(variant_ids)
            
            for i in range(length):
                temp = []
                

                values = {
                    'product_id': int(variant_ids[i]),
                    'line_id': line_id,
                    'product_uom_qty': int(variant_quantity[i]),
                    'price_unit': 0
                }
                temp.append((0, 0, values))
                order.write({'order_line': temp})

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity
        from_currency = order.company_id.currency_id
        to_currency = order.pricelist_id.currency_id

        if not display:
            return value

        value['website_sale.cart_lines'] = request.env['ir.ui.view'].render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            # compute_currency deprecated (not used in view)
            'compute_currency': lambda price: from_currency._convert(
                price, to_currency, order.company_id, fields.Date.today()),
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view'].render_template(
            "website_sale.short_cart_summary", {
                'website_sale_order': order,
                'compute_currency': lambda price: from_currency._convert(
                    price, to_currency, order.company_id, fields.Date.today()),
            })
        return value

    @http.route('/check/product/variants', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
    def Check_product_variant_for_selection(self, **kw):
        product_id=request.env['product.product'].sudo().search([('id','=',kw['product_id'])])
        count=0
        check_no_of_bombs_ids=0
        if(product_id.bom_count>0):
            bom_id = request.env['mrp.bom'].sudo().search([('product_id', '=', product_id.id)])
            for rec in bom_id.bom_line_component_ids:
                check_no_of_bombs_ids=check_no_of_bombs_ids+1

            count=count+1
        
        values={
            'count':count,
            'check_no_of_bombs_ids':check_no_of_bombs_ids
        }
        return json.dumps(values)



    @http.route(['/product_configurator/get_combination_info'], type='json', auth="user", methods=['POST'])
    def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
        combination = request.env['product.template.attribute.value'].browse(combination)
        pricelist = self._get_pricelist(pricelist_id)
        ProductTemplate = request.env['product.template']
        if 'context' in kw:
            ProductTemplate = ProductTemplate.with_context(**kw.get('context'))
        product_template = ProductTemplate.browse(int(product_template_id))
        res = product_template._get_combination_info(combination, int(product_id or 0), int(add_qty or 1), pricelist)
        if 'parent_combination' in kw:
            parent_combination = request.env['product.template.attribute.value'].browse(kw.get('parent_combination'))
            if not combination.exists() and product_id:
                product = request.env['product.product'].browse(int(product_id))
                if product.exists():
                    combination = product.product_template_attribute_value_ids
            res.update({
                'is_combination_possible': product_template._is_combination_possible(combination=combination, parent_combination=parent_combination),
            })
        if product_id:
            product_detail=request.env['product.product'].sudo().search([('id','=',res["product_id"])])
            if product_detail.product_documents_ids:
                for rec in product_detail.product_documents_ids:
                    if rec.public:
                        res.update({"document":True})
                    else:
                        res.update({"document":False})    
            else:
                res.update({"document":False})
            if product_detail.unpublish_product==False:
                res.update({"publish":True})
                
            else:
                res.update({"publish":False})
                
        return res
    @http.route(['/product_configurator/get_combination_info_website'], type='json', auth="public", methods=['POST'], website=True)
    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, **kw):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """

        res={}
        product_template = request.env['product.template'].search([('id','=',product_template_id)])
        if 'seleted_attribute' in kw:
            if kw['selector'] != 'none':
                temp=product_template._get_valid_product_template_attribute_lines();
                temp_list_value=[]
                for rec in temp:
                    if rec.attribute_id.id != int(kw['seleted_attribute']):
                        temp=[]
                        for value in rec.product_template_value_ids:
                            temp.append(value.id)
                        temp_list_value.append(temp)
                    else:
                        temp_list_value.append([int(kw['selector'])])
                combinations_all = list(itertools.product(*temp_list_value))
                new_list=[]
                product_ids=[]
                for i in combinations_all:
                    data= self.get_combination_info(product_template_id, product_id, list(i), add_qty, **kw)
                    if data['publish']==True:
                            new_list.append(i)
                            product_ids.append(data['product_id'])
                product_variant_ids=request.env['product.product'].search([('id','in',product_ids)])
                temp_list=[]
                for rec in product_variant_ids:
                    for attribute in rec.attribute_value_ids:
                        if attribute.id not in temp_list:
                            temp_list.append(attribute.id)
                # temp_list.remove(int(kw['selector']))
                final_temp_lis=[]
                final_dict={}
                temp=product_template._get_valid_product_template_attribute_lines();
                for rec in temp:
                    temp=[]
                    final_temp_lis=[]
                    if int(kw['seleted_attribute']) != rec.attribute_id.id:
                        for attribute in rec.product_template_value_ids:
                            if attribute.product_attribute_value_id.id in temp_list:
                                if rec.uom_ids:
                                    final_temp_lis.append([attribute.id,attribute.name,rec.uom_ids.name])
                                else:
                                    final_temp_lis.append([attribute.id,attribute.name,''])
                        final_dict[rec.attribute_id.id]=final_temp_lis
                current_product_id=request.env['product.product'].search([('id','=',product_id)])
                if current_product_id.uom_id:

                    res.update({
                    'product_id': product_id,
                    'product_template_id': product_template_id,
                    'final_dict':final_dict,
                    'uom_id':current_product_id.sudo().uom_id.name,
                    'combination':combination
                    })

                else:
                    res.update({
                    'product_id': product_id,
                    'product_template_id': product_template_id,
                    'final_dict':final_dict,
                    'uom_id':False,
                    'combination':combination
                    })

            else:
                temp_final=[]
                for rec in product_template._get_valid_product_template_attribute_lines():
                    temp=[]
                    for value_ids in rec.product_template_value_ids:
                        temp.append(value_ids.id)
                    temp_final.append(temp)
                combinations_all = list(itertools.product(*temp_final))
                new_list=[]
                product_ids=[]
                for i in combinations_all:
                    data= self.get_combination_info(product_template, product_template.product_variant_id, list(i), 1, **kw)
                    if data['publish']==True:
                        new_list.append(i)
                        product_ids.append(data['product_id'])
                product_product_ids=request.env['product.product'].search([('id','in',product_ids)])
                temp_list=[]
                final_temp_list=[]
                for rec in product_product_ids:
                    for attribute in rec.attribute_value_ids:
                        for value_ids in attribute:
                            final_temp_list.append(value_ids.id)
                temp=[]
                temp_attribute_ids=[]
                product_temp_ids=product_template._get_valid_product_template_attribute_lines();
                for rec in product_temp_ids:  
                    if rec.attribute_id.id==int(kw['seleted_attribute']):
                        for attributes_value in rec.product_template_value_ids:
                            if attributes_value.product_attribute_value_id.id in final_temp_list:
                                temp.append([attributes_value.id,attributes_value.name])
                        temp_attribute_ids.append(temp)
                res.update({
                'product_id': product_id,
                'product_template_id': product_template_id,
                'temp':temp,
                'combination':combination,
                })
        else:
            res.update({
                'product_id': product_id,
                'product_template_id': product_template_id,
                
                'combination':combination
                })


        
        # for rec in product_template.attribute_line_ids:
        #     if rec.attribute_id.id != int(kw['seleted_attribute']):
        #         temp=[]
        #         for value_ids in rec.value_ids:
        #             temp.append(value_ids.id)
        #         temp_list_value.append(temp)
        # temp_list_value.append([int(kw['selector'])])
        # combinations_all = list(itertools.product(*temp_list_value))
        # for i in combinations_all:
        #     data= self.get_combination_info(product_template_id, product_id, list(i), add_qty, **kw)

        kw.pop('pricelist_id')
        if None in combination:
            # res ={
            # 'product_id': product_id,
            # 'product_template_id': product_template_id
            # }
            if request.env.ref('website_product_detail_page.website_select_option', raise_if_not_found=False):  # IF for compatibility 12.0
                res.update(carousel=request.env['ir.ui.view'].render_template('website_product_detail_page.website_select_option', values={
                'product': request.env['product.template'].browse(res['product_template_id']),
                'product_variant': request.env['product.product'].browse(res['product_id']),
            }))
        else:
            res.update(self.get_combination_info(product_template_id, product_id, combination, add_qty, request.website.get_current_pricelist(), **kw))
            if request.env.ref('website_product_detail_page.product_data_change_through_javascript_in_website', raise_if_not_found=False):
                res.update(carousel=request.env['ir.ui.view'].render_template('website_product_detail_page.product_data_change_through_javascript_in_website', values={
                    'product': request.env['product.template'].browse(res['product_template_id']),
                    'product_variant': request.env['product.product'].browse(res['product_id']),
                }))
        return res
