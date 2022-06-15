# -*- coding: utf-8 -*-
import datetime
import json
import urllib
import werkzeug
from odoo import http, SUPERUSER_ID
from odoo.http import request

PPG = 2


class FindProduct(http.Controller):

    @http.route(['/find-a-product', '/find-a-product/page/<int:page>'], type='http', auth="public", website=True)
    def find_a_product(self, search_product='', parent_category='', child_categ_1='', child_categ_2='', page=0, ppg=False, **post):
        if post.get('search'):
            post.update({'search_product_by_name': post.get('search')})
        search_product = post.get('search_product_by_name') or post.get('search_product_by_stock') or post.get('search') 

        PPG = 20000 if 'all' == request.env['website'].search(
            [], limit=1).ppp_on_find else int(request.env['website'].search([], limit=1).ppp_on_find)

        sub_category_1_ids = request.env['product.public.category'].sudo().search([('parent_id', '=', int(parent_category))]) if parent_category else []
        parent_category_ids = request.env['product.public.category'].sudo().search([('parent_id', '=', False)])
        sub_category_2_ids = request.env['product.public.category'].sudo().search([('parent_id', '=', int(child_categ_1))]) if (parent_category and child_categ_1) else []

        domain = [('website_published', '=', True)]
        if not search_product and not parent_category:
            domain.append(('id', '!=', False))
        else:
            if child_categ_2 and child_categ_1 and parent_category:
                if search_product:
                    if  post.get('search_product_by_name') and not post.get('search_product_by_stock'):
                        domain += ['|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('public_categ_ids', 'child_of', int(child_categ_2))
                        ]
                    elif not post.get('search_product_by_name') and post.get('search_product_by_stock'):
                        domain += [
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(child_categ_2))
                        ]
                    else:
                        domain += ['|','|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(child_categ_2))
                        ]
                else:
                    domain += [('public_categ_ids', 'child_of', int(child_categ_2))]
            elif child_categ_1 and parent_category:
                if search_product:
                    if  post.get('search_product_by_name') and not post.get('search_product_by_stock'):
                        domain += ['|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('public_categ_ids', 'child_of', int(child_categ_1))
                        ]
                    elif not post.get('search_product_by_name') and post.get('search_product_by_stock'):
                        domain += [
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(child_categ_1))
                        ]
                    else:
                        domain += ['|','|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(child_categ_1))
                        ]
                else:
                    domain += [('public_categ_ids', 'child_of', int(child_categ_1))]
            elif parent_category:
                if search_product:
                    if  post.get('search_product_by_name') and not post.get('search_product_by_stock'):
                        domain += ['|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('public_categ_ids', 'child_of', int(parent_category))
                        ]
                    elif not post.get('search_product_by_name') and post.get('search_product_by_stock'):
                        domain += [
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(parent_category))
                        ]
                    else:
                        domain += ['|','|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(parent_category))
                        ]
                else:
                    domain += [('public_categ_ids', 'child_of', int(parent_category))]
            else:
                if  post.get('search_product_by_name') and not post.get('search_product_by_stock'):
                    domain += [
                        ('name', 'ilike', post.get('search_product_by_name'))
                    ]
                elif not post.get('search_product_by_name') and post.get('search_product_by_stock'):
                    domain += [('default_code', 'ilike', post.get('search_product_by_stock'))]
                else:    
                    domain += ['|','|',
                        ('name', 'ilike', post.get('search_product_by_name')),
                        ('website_name', 'ilike', post.get('search_product_by_name')),
                        ('default_code', 'ilike', post.get('search_product_by_stock'))
                    ]
        
        if parent_category:
            post['parent_category'] = parent_category
        if child_categ_1:
            post['child_categ_1'] = child_categ_1
        if child_categ_2:
            post['child_categ_2'] = child_categ_2
        if search_product:
            post['search_product'] = search_product

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = int(PPG)
            post["ppg"] = ppg
        else:
            ppg = PPG

        product_obj = request.env['product.template']

        product_count = product_obj.search_count(domain)
        pager = request.website.pager(
            url='/find-a-product', total=product_count, page=page, step=int(ppg), scope=7, url_args=post)
        if 'all' == request.env['website'].search([], limit=1).ppp_on_find:
            products = product_obj.search(domain,  offset=pager['offset'])
        else:
            products = product_obj.search(domain, limit=int(ppg), offset=pager['offset'])
            
        

        values = {
            'parent_category': parent_category,
            'search_product': search_product,
            'search_product_by_stock': post.get('search_product_by_stock'),
            'search_product_by_name': post.get('search_product_by_name'),
            'pager': pager,
            'products': products,
            'parent_category_ids': parent_category_ids,
            'sub_category_1_ids': sub_category_1_ids,
            'sub_category_2_ids': sub_category_2_ids,
            'child_categ_1': child_categ_1,
            'child_categ_2': child_categ_2 
        }

        return request.render('website_find_a_product.find_a_product', values)



    @http.route(['/find-a-product-menu/<model("product.public.category"):categ_id>'], type='http', auth="public", website=True)
    def find_a_product_menu(self, search_product='', parent_category='', child_categ_1='', child_categ_2='', page=0, ppg=False, **post):
        if post.get('categ_id'):
            if post.get('categ_id').parent_id:
                if post.get('categ_id').parent_id.parent_id:
                    child_categ_2=post.get('categ_id').id
                    child_categ_1 = post.get('categ_id').parent_id.id
                    parent_category = post.get('categ_id').parent_id.parent_id.id
                    
                else:
                    child_categ_1=post.get('categ_id').id
                    parent_category = post.get('categ_id').parent_id.id
            else:
                parent_category=post.get('categ_id').id
        if not post.get('search_product_by_name'):
            post['search_product_by_name']=''
        if post.get('search'):
            post.update({'search_product_by_name': post.get('search')})
        search_product = post.get('search_product_by_name') or post.get('search_product_by_stock') or post.get('search') 

        PPG = 20000 if 'all' == request.env['website'].search(
            [], limit=1).ppp_on_find else int(request.env['website'].search([], limit=1).ppp_on_find)

        sub_category_1_ids = request.env['product.public.category'].sudo().search([('parent_id', '=', int(parent_category))]) if parent_category else []
        parent_category_ids = request.env['product.public.category'].sudo().search([('parent_id', '=', False)])
        sub_category_2_ids = request.env['product.public.category'].sudo().search([('parent_id', '=', int(child_categ_1))]) if (parent_category and child_categ_1) else []
        website_menu_name = None
        website_menu_comment = None
        website_menu_image = None
        if parent_category:
            search_record_name = request.env['website.menu'].sudo().search([('website_product_catag_id', '=', int(parent_category))])    
            for rec in search_record_name:
                website_menu_name = rec.name
                website_menu_comment = rec.comment
                website_menu_image = rec.image

        if child_categ_1:    
            search_record_name_child = request.env['website.menu'].sudo().search([('website_product_catag_id', '=', int(child_categ_1))])    
            for rec in search_record_name_child:
                website_menu_name_child = rec.name
                website_menu_comment_child = rec.comment
                website_menu_image_child = rec.image
             
        domain = [('website_published', '=', True)]
        if not search_product and not parent_category:
            domain.append(('id', '!=', False))
        else:
            if child_categ_2 and child_categ_1 and parent_category:
                if search_product:
                    if  post.get('search_product_by_name') and not post.get('search_product_by_stock'):
                        domain += ['|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('public_categ_ids', 'child_of', int(child_categ_2))
                        ]
                    elif not post.get('search_product_by_name') and post.get('search_product_by_stock'):
                        domain += [
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(child_categ_2))
                        ]
                    else:
                        domain += ['|','|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(child_categ_2))
                        ]
                else:
                    domain += [('public_categ_ids', 'child_of', int(child_categ_2))]
            elif child_categ_1 and parent_category:
                if search_product:
                    if  post.get('search_product_by_name') and not post.get('search_product_by_stock'):
                        domain += ['|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('public_categ_ids', 'child_of', int(child_categ_1))
                        ]
                    elif not post.get('search_product_by_name') and post.get('search_product_by_stock'):
                        domain += [
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(child_categ_1))
                        ]
                    else:
                        domain += ['|','|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(child_categ_1))
                        ]
                else:
                    domain += [('public_categ_ids', 'child_of', int(child_categ_1))]
            elif parent_category:
                if search_product:
                    if  post.get('search_product_by_name') and not post.get('search_product_by_stock'):
                        domain += ['|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('public_categ_ids', 'child_of', int(parent_category))
                        ]
                    elif not post.get('search_product_by_name') and post.get('search_product_by_stock'):
                        domain += [
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(parent_category))
                        ]
                    else:
                        domain += ['|','|',
                            ('name', 'ilike', post.get('search_product_by_name')),
                            ('website_name', 'ilike', post.get('search_product_by_name')),
                            ('default_code', 'ilike', post.get('search_product_by_stock')),
                            ('public_categ_ids', 'child_of', int(parent_category))
                        ]
                else:
                    domain += [('public_categ_ids', 'child_of', int(parent_category))]
            else:
                if  post.get('search_product_by_name') and not post.get('search_product_by_stock'):
                    domain += [
                        ('name', 'ilike', post.get('search_product_by_name'))
                    ]
                elif not post.get('search_product_by_name') and post.get('search_product_by_stock'):
                    domain += [('default_code', 'ilike', post.get('search_product_by_stock'))]
                else:    
                    domain += ['|','|',
                        ('name', 'ilike', post.get('search_product_by_name')),
                        ('website_name', 'ilike', post.get('search_product_by_name')),
                        ('default_code', 'ilike', post.get('search_product_by_stock'))
                    ]
        
        if parent_category:
            post['parent_category'] = parent_category
        if child_categ_1:
            post['child_categ_1'] = child_categ_1
        if child_categ_2:
            post['child_categ_2'] = child_categ_2
        if search_product:
            post['search_product'] = search_product

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = int(PPG)
            post["ppg"] = ppg
        else:
            ppg = PPG

        product_obj = request.env['product.template']

        product_count = product_obj.search_count(domain)
        pager = request.website.pager(
            url='/find-a-product-menu', total=product_count, page=page, step=int(ppg), scope=7, url_args=post)
        if 'all' == request.env['website'].search([], limit=1).ppp_on_find:
            products = product_obj.search(domain,  offset=pager['offset'])
        else:
            products = product_obj.search(domain, limit=int(ppg), offset=pager['offset'])

        values = {
            'parent_category': str(parent_category),
            'search_product': search_product,
            'search_product_by_stock': post.get('search_product_by_stock'),
            'search_product_by_name': post.get('search_product_by_name'),
            'pager': pager,
            'products': products,
            'parent_category_ids': parent_category_ids,
            'sub_category_1_ids': sub_category_1_ids,
            'sub_category_2_ids': sub_category_2_ids,
            'child_categ_1': str(child_categ_1),
            'child_categ_2': str(child_categ_2),
            'website_menu_name': str(website_menu_name),
            'website_menu_comment': str(website_menu_comment),
            'website_menu_image': website_menu_image,
        }
        
        if child_categ_1:
            values.update({'website_menu_name_child': str(website_menu_name_child)})
            values.update({'website_menu_comment_child': str(website_menu_comment_child)})
            values.update({'website_menu_image_child': website_menu_image_child})

        return request.render('website_find_a_product.find_a_product_menu', values)
