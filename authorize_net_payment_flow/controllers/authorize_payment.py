# -*- coding: utf-8 -*-
from odoo import http, tools, _, fields
from odoo.http import content_disposition, Controller, request, route
import datetime
import base64
# from odoo.exceptions import AccessError
# from odoo.addons.portal.controllers.portal import CustomerPortal

# from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.mail import _message_post_helper
# from odoo.addons.ct_web_checkout.controllers.main import ProductRedirect

class AuthorizePaymentController(http.Controller):

    # Purchase Process for payment

    @http.route(['/Add_update/card','/Add_update/card/<int:order>'], type='http',auth='user', website=True)
    def add_update_card(self, order=None,**kw):
        # {'debit_card_no': '3245678544567545', 'card_holder_name': 'fsdfsdsfs', 'month': '04', 'year': '2018', 'cvv_code': '123', 'submitted': '1', 'sale_order_id': '5', 'billing_address_id': '11'}
        sale_order = False
        if order:
            sale_order = order
        if kw.get('sale_order_id'):    
            sale_order = int(kw.get('sale_order_id'))
        order_sale = request.env['sale.order'].sudo().search([('id', '=', sale_order)])
        billings = []
        warning = {}
        if kw.get('submitted'):
            if order_sale.partner_id.customer_profile_id:
                res = order_sale.partner_id.create_add_payment_profile(kw,order_sale.partner_id.customer_profile_id)        
                if res.get('err_msg'):
                    warning['card_auth_err'] = res.get('err_msg') 
            else:    
                res = order_sale.partner_id.create_partner_authorize_profile(kw) 
                if res.get('err_msg'):
                    warning['card_auth_err'] = res.get('err_msg')

        Partner = order_sale.partner_id.with_context(show_address=1).sudo()
        billings = Partner.search([
                ("parent_id", "=", order_sale.partner_id.id),
                ("type_extend", "=", "invoice")], order='default_address desc')

        values = {
                'order_sale': order_sale,
                'billings': billings,
                'warning': warning
            }

        if warning:
            values.update({
                    'debit_card_no': kw.get('debit_card_no',''),
                    'card_holder_name': kw.get('card_holder_name',''),
                    'month': kw.get('month',''),
                    'year': kw.get('year',''),
                    'billing_address_id': kw.get('billing_address_id'),
                    'warning': warning,
                    'cvv_code': kw.get('cvv_code')
                })    
        
        return request.render("authorize_net_payment_flow.add_update_card",values)

    @http.route(['/quote/purchase/<int:order>'], type='http', auth="user", website=True)
    def quotation_purchase(self, order=None, **kw):
        credit_card_detail_obj = request.env['credit.card.detail']
        warning = False
        if kw.get('card_value_add_or_change'):
            values = {
                    'month': kw.get('month'),
                    'year': kw.get('year'),
                    'debit_card_no': kw.get('debit_card_no'),
                    'card_holder_name': kw.get('card_holder_name')
            }
            if kw.get('card_value_add_or_change') == 'change':
                credit_card_details = credit_card_detail_obj.sudo().search([
                    ('id', '=', kw.get('credit_card_detail_id'))])

                credit_card_details.sudo().write(values)

            if kw.get('card_value_add_or_change') == 'add':
                credit_card_details = credit_card_detail_obj.sudo().search([
                    ('debit_card_no', '=', kw.get('debit_card_no'))])
                if not credit_card_details:
                    values['partner_id'] = kw.get('partner_id_model')
                    credit_card_details = credit_card_detail_obj.sudo().create(values)
                else:
                    warning = 'Card Number is Already Exists'    
      
            if kw.get('card_value_add_or_change') == 'remove':
                credit_card_details = credit_card_detail_obj.sudo().search([
                    ('id', '=', kw.get('credit_card_detail_id'))])
                if credit_card_details:
                    credit_card_details.sudo().unlink() 
        order_sale = request.env['sale.order'].sudo().search([('id', '=', order)])
        
        for card_detail_ids in order_sale.partner_id.partner_card_detail_ids:
            number = 'XXX XXXX XXX '+ card_detail_ids.debit_card_no[-4:]
            

            setattr(card_detail_ids, 'debit_card_no_encrypt', number)
        billings = []
        Partner = order_sale.partner_id.with_context(show_address=1).sudo()
        billings = Partner.search([
                ("parent_id", "=", order_sale.partner_id.id),
                ("type_extend", "=", "invoice")], order='default_address desc')

        values = {
                'order_sale': order_sale,
                'billings': billings,
                'credit_card_details': order_sale.partner_id.partner_card_detail_ids,
                'warning': warning
            }
        return request.render("website_my_account.portal_purchase_approved", values)


    @http.route(['/approve/purchase'], type='http', auth="user", website=True)
    def approved_purchase(self, order=None, **kw):
        order_sale = False
        if kw.get('sale_order_id'):
            order_sale = request.env['sale.order'].sudo().search([('id', '=', kw.get('sale_order_id'))])
            if order_sale.signature == 'yes':
                values ={
                    'sale_order' : order_sale
                }
                return request.render("website_my_account.portal_signature", values)
            else:
                order_sale.write({'is_portal_authorised':True}) 
                return request.redirect('/my/orders/%s' %(order_sale.id))     

    @http.route(['/portal/signature'], type='json', auth="user", website=True)
    def portal_signature(self, order_id=None, token=None, sign=None, customer_name=None, **kw):
        
        warning = False
        values = False
        Order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        attachments = [('signature.png', base64.b64decode(sign))] if sign else [] 
        message = _('Order signed by %s') % (customer_name)
        # if token != Order.access_token or Order.require_payment:
        #     return request.render('website.404')
        _message_post_helper(message=message, res_id=Order.id, res_model='sale.order', attachments=attachments, **({'token': token, 'token_field': 'access_token'} if token else {}))
        values = {
            'order_id': order_id
        }
        Order.write({'is_portal_authorised':True})   
        return values
