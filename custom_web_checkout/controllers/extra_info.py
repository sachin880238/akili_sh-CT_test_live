import datetime
import json
import urllib
import base64
import werkzeug
from odoo import http, SUPERUSER_ID
from odoo.http import request


class ExtraInfo(http.Controller):

    # extra information page
    @http.route(['/extra/custom_info'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def extra_info_custom(self, **kw):
        order = request.website.sale_get_order()
        if not order:
            return request.render('website.404')
        error = {}
        att_obj = request.env['ir.attachment']
        attachments = att_obj.sudo().search(
            [('res_model', '=', 'sale.order'), ('res_id', '=', order.id)])
        if 'upload_attachment' in kw:
            datas = ''
            if hasattr(kw.get('slae_order_doc'), 'filename'):
                datas = kw.get('slae_order_doc').read()

            if datas:
                attachment = att_obj.sudo().create({
                    'name': order.name,
                    'type': 'binary',
                    'datas':  base64.b64encode(datas),
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'datas_fname': kw.get('slae_order_doc').filename
                })
                attachments += attachment
        if 'submitted' in kw:
            if not kw.get('customer_priority'):
                error['customer_priority'] = "Please Select the priority."     
            else:
                order.message_post(body=kw.get('note'))
                order.client_order_ref = kw.get('client_order_ref')
                order.customer_priority = kw.get('customer_priority')
                order.note = kw.get('note')
                return request.redirect('/shop/review')

        render_values = {
            'order': order,
            'error': error,
            'order_attachments': attachments,
            'client_order_ref': kw.get('client_order_ref_1'),
            'customer_priority': kw.get('customer_priority_1'),
            'note': kw.get('note_1')
        }
             
        return request.render("custom_web_checkout.extra_info_lee", render_values)

    @http.route(['/extra/custom_info/save_document'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def extra_info_custom_data(self, **kw):
        order = request.website.sale_get_order()
        if not order:
            return request.render('website.404')
        error = {}
        att_obj = request.env['ir.attachment']
        attachments = att_obj.sudo().search(
            [('res_model', '=', 'sale.order'), ('res_id', '=', order.id)])
        if 'upload_attachment' in kw:
            datas = ''
            if hasattr(kw.get('slae_order_doc'), 'filename'):
                datas = kw.get('slae_order_doc').read()

            if datas:
                attachment = att_obj.sudo().create({
                    'name': order.name,
                    'type': 'binary',
                    'datas':  base64.b64encode(datas),
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'datas_fname': kw.get('slae_order_doc').filename
                })
                attachments += attachment
        if 'submitted' in kw:
            if not kw.get('customer_priority'):
                error['customer_priority'] = "Please Select the priority."     
            else:
                order.message_post(body=kw.get('note'))
                order.client_order_ref = kw.get('client_order_ref')
                order.customer_priority = kw.get('customer_priority')
                order.note = kw.get('note')
                return request.redirect('/shop/review')

        # render_values = {
        #     'order': order,
        #     'error': error,
        #     'order_attachments': attachments,
        #     'client_order_ref': kw.get('client_order_ref_1'),
        #     'customer_priority': kw.get('customer_priority_1'),
        #     'note': kw.get('note_1')
        # }
             
        return
    
    @http.route(['/delete_attachment/cart'], type='json', auth="user", methods=['POST'])
    def configure_deletw_attachment(self,  **kw):
        attachment_id=kw.get('attachment_id')
        att_obj = request.env['ir.attachment']
        attachments = att_obj.sudo().search(
            [('res_model', '=', 'sale.order'), ('id', '=', attachment_id)])
        attachments.unlink()

        return kw

    @http.route(['/fetch/color/record'], type='json', auth="public", methods=['GET', 'POST'])
    def fetchRecord(self,  **kw):
        if kw['name'] == 'Website Header Icon Email Config Setting':
            record_id=request.env['system.config'].sudo().search([('name','=','Website Header Icon Email Config Setting')])
            cross_id = request.env['system.config'].sudo().search([('name','=','Website Header Color Config Setting')])
        if kw['name'] == 'Website Header Icon Call Config Setting':
            record_id=request.env['system.config'].sudo().search([('name','=','Website Header Icon Call Config Setting')])
            cross_id = request.env['system.config'].sudo().search([('name','=','Website Header Color Config Setting')])
        
        data={'html_data':record_id.taxt_email,
                'header_color':record_id.mail_header_color,
                'header_data':record_id.main_heading_email,
                'cross_color':cross_id.web_header_content_color,
            }

        
        return data

    @http.route(['/fetch/web-color/record'], type='json', auth="public", methods=['GET', 'POST'])
    def WebHeaderRecord(self,  **kw):
        if kw['name'] == 'Website Header Color Config Setting':
            record_id=request.env['system.config'].sudo().search([('name','=','Website Header Color Config Setting')])

        data={
                'web_header_bckgrnd_color':record_id.web_header_bckgrnd_color,
                'web_header_content_color':record_id.web_header_content_color,
            }  

        return data 

    @http.route(['/fetch/current_cart'], type='json', auth="public", methods=['POST'],website=True)
    def CurrentCart(self,  **kw):
        user_id = request.env.user
        partner = request.env.user.partner_id
        sale_id = order = request.website.sale_get_order()
        data = request.env['ir.ui.view'].render_template("website_custom_menu.cart_modal",{
             'sale_id':sale_id,
            })
        return data       
           
    @http.route(['/extra/save_order_detail'], type='json', methods=['GET', 'POST'], auth="public", website=True)
    def save_order_detail(self, **kw):
        order = request.website.sale_get_order()
        vals = {}

        if order:
            order.client_order_ref = kw.get('client_order_ref')
            order.customer_priority = kw.get('customer_priority')
            priority = order.customer_priority
            if priority == "estimate":
                order.priority = 'x'
            elif priority == "plan":
                order.priority = 'xx'
            elif priority == "ready":
                order.priority = 'xxx'
            order.note = kw.get('note')

            vals = {
                'client_order_ref': order.client_order_ref,
                'customer_priority': priority,
                'note': order.note
            }

        return vals
