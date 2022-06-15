# -*- coding: utf-8 -*-
from collections import OrderedDict

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import itertools


class ProductRedirect(WebsiteSale):


    def get_attribute_value_ids(self, product):
        """ list of selectable attributes of a product

        :return: list of product variant description
           (variant id, [visible attribute ids], variant price, variant sale price)
        """
        # product attributes with at least two choices
        product = product.with_context(quantity=1)

        visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
        to_currency = request.website.get_current_pricelist().currency_id
        attribute_value_ids = []
        for variant in product.product_variant_ids:
            if to_currency != product.currency_id:
                price = variant.currency_id.compute(variant.website_public_price, to_currency)
            else:
                price = variant.website_public_price
            visible_attribute_ids = [v.id for v in variant.attribute_value_ids if v.attribute_id.id in visible_attrs_ids]
            attribute_value_ids.append([variant.id, visible_attribute_ids, variant.website_price, price])
        return attribute_value_ids

    @http.route(['/get-product-detail-from-id'], type='json', auth="public", website=True)
    def get_product_detail_from_id(self, model=None, product_id=None, **kwargs):

        data = {}

        if (model and product_id):

            data = request.env[model].sudo().search_read([('id','=',product_id)])
        return data


    @http.route(['/get-atttribute-detail-from-template'], type='json', auth='public', website=True)
    def get_attribute_detail_from_template(self, product_tmpl_id,seq=0):
        
        res = {}

        product_tmpl_id = request.env['product.template'].browse(product_tmpl_id)
        product_attr_selection = OrderedDict()
        attribute_ids=product_tmpl_id._get_valid_product_template_attribute_lines();
        temp_list=[]
        for attribute_line_data in attribute_ids:
            temp_list.append(attribute_line_data.product_template_value_ids.ids)
        possible_combinations=list(itertools.product(*temp_list))
        final_combination_temp=[]
        for combination_data in possible_combinations:
            combination = request.env['product.template.attribute.value'].browse(list(combination_data))
            product_data=product_tmpl_id._get_combination_info(combination,0, 1, False)
            product_id=request.env['product.product'].browse(product_data['product_id'])
            if product_id.unpublish_product == False:
                final_combination_temp.extend(list(combination_data))
        publish_value = []
        [publish_value.append(x) for x in final_combination_temp if x not in publish_value]
        for attribute_line_id in attribute_ids:
            values = []
            
            for value_id in attribute_line_id.product_template_value_ids:
                if value_id.id in publish_value:
                    value = [value_id.id, value_id.name]
                    values.append(value)
            product_attr_selection[attribute_line_id.attribute_id.name] = [attribute_line_id.attribute_id.id, values]
        value=self.get_attribute_value_ids(product_tmpl_id)
        res.update({
            'product_attr_selection': product_attr_selection,
            'attribute_value_ids': value,
            'seq':seq
        })
        return res


    @http.route(['/get-attribute-value-from-tmpl-id'], type='json', auth='public', website=True)
    def get_attribute_value_from_template(self, product_tmpl_id,collect_comb=[], **post):
        product_tmpl_id = request.env['product.template'].browse(product_tmpl_id)
        if 0 not in collect_comb:
            combination = request.env['product.template.attribute.value'].browse(collect_comb)
            product_data=product_tmpl_id._get_combination_info(combination,0, 1, False)
        else:
            product_data=False
        
        return [self.get_attribute_value_ids(product_tmpl_id),product_data]

    @http.route(['/get-doc-detail-from-product-id'], type='json', auth='public', website=True)
    def get_document_detail_from_product_id(self, product_id, **post):
        product_id = request.env['product.product'].browse(product_id)
        product_documents_val = []
        for document_id in product_id.product_documents_ids:
            doc_val = {}
            if document_id.public:
                doc_val.update({
                    'datas_fname': document_id.name,
                    'product_description': document_id.description,
                    'id': document_id.id
                })
                product_documents_val.append(doc_val)

        vals = {
            'id': product_id.id,
            'display_name': product_id.display_name,
            'have_published_document': product_id.have_published_document(),
            'product_documents_val': product_documents_val 
        }
        return vals
