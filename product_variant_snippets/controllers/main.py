# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductRedirect(WebsiteSale):

    @http.route(['/get-product-detail-from-id'], type='json', auth="public", website=True)
    def get_product_detail_from_id(self, model=None, product_id=None, **kwargs):

        data = {}

        if (model and product_id):

            data = request.env[model].sudo().search_read([('id','=',product_id)])
            
        return data



    @http.route(['/web/product_templates'], type='json', auth="user")
    def call_kw(self, model, method, args, kwargs, path=None):
        return True
