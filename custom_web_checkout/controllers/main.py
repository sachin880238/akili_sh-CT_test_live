# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)


try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


class ProductRedirect(WebsiteSale):

    # due to duplication of method i comment
    # @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    # def product(self, product, product_variant=None, category='', search='', **kwargs):
    #     res = super(ProductRedirect, self).product(product=product, category=category, search=search, **kwargs)
    #     if res.qcontext.get('keep'):
    #         res.qcontext.get('keep').__dict__['path'] = '/find-a-product'
    #     if kwargs.get('variant-id'):

    #         product_variant = request.env['product.product'].sudo().browse(int(kwargs.get('variant-id')))

    #         res.qcontext.update({
    #             'variant_id': kwargs.get('variant-id'),
    #             'product': product_variant,
    #             'selected_product_variant': product_variant and True
    #         })

    #     return res

    @http.route(['/shop/save_cart'], type='http', auth="public", methods=['POST'], website=True)
    def save_cart(self, **kw):
        if 'save_note' in kw:
            order = request.website.sale_get_order(force_create=1)
            order.write({'is_cart_saved': True, 'cart_state': 'saved', 'save_note': kw['save_note']})
            order.message_post(body=kw.get('Cart Saved'))
        request.session.pop('sale_order_id')
        # request.env.user.partner_id.last_website_so_id = False
        return request.redirect()

    @http.route(['/check/existing'], type='http', auth="public", website=True)
    def check_email_exist(self, **post):
        return request.render('custom_web_checkout.check_email_exist', {})

    @http.route(['/check-existing-email'], type='http', auth="public", methods=['POST'], website=True)
    def check_existing_email(self, **post):
        vals = {}
        if post.get('email'):
            user = request.env['res.users'].sudo().search(
                [('login', '=', post.get('email'))], limit=1)

            if user:
                vals.update({'login': post.get('email')})
                return request.render('lee_auth.lee_auth_login', vals)

            vals.update({
                'payment_redirect': '/shop/checkout',
                'login': post.get('email')
            })
            encoded_query_string = urlencode(vals)
            return request.redirect('/web/signup?' + encoded_query_string)

        return request.render('custom_web_checkout.check_email_exist', vals)

    @http.route(['/check-number-is-valid'], type='json', auth="public", methods=['POST'])
    def check_number_is_valid(self, phone='', **post):
        res = {}
        if (phone == '9904636045'):
            res.update({
                'valid': True
            })
        res.update({
            'valid': True
        })
        return res

    # Address customization

    @http.route(['/shop/partner/remove'], type='json', auth="public", methods=['POST'], website=True)
    def partner_remove(self, partner_id=None, type_extend=None, **kwars):
        if partner_id:
            try:
                partner = request.env['res.partner'].sudo().browse(partner_id)
                partner_count = request.env['res.partner'].search_count([
                    ('type_extend', '=', partner.type_extend),
                    ('parent_id', '=', partner.parent_id.id),
                    ('active', '=', True)])
                if partner_count > 1:
                    partner.write({'active': False})
                    return {'result': True}
                else:
                    return {'result': False, 'error_message': ['PLease create new address after remove curerent address']}
            except Exception as e:
                return {'result': False, 'message': ['You cannot remove this contact', str(e)]}
        return {'result': False, 'error_message': ['Contact not found']}

    def checkout_values(self, **kw):
        order = request.website.sale_get_order(force_create=1)
        shippings = []
        billings = []
        contacts = []
        partner_id = False
        default_address = False
        if order.partner_id != request.website.user_id.sudo().partner_id:
            Partner = order.partner_id.with_context(show_address=1).sudo()
            if kw.get('partner_id'):
                partner_id = Partner.search([('id', '=', int(kw.get('partner_id')))])
                partner_id.sudo().write({'default_address': True})
            shippings = Partner.search([
                ("parent_id", "=", order.partner_id.id),
                ("type_extend", "=", "delivery")], order='default_address desc')
            billings = Partner.search([
                ("parent_id", "=", order.partner_id.id),
                ("type_extend", "=", "invoice")], order='default_address desc')
            contacts = Partner.search([
                ("parent_id", "=", order.partner_id.id),
                ("type_extend", "=", "contact")], order='default_address desc')
            
            if shippings:
                default_address = [shipping for shipping in shippings if shipping.default_address == True and shipping != partner_id]
                if partner_id and partner_id.id in shippings.mapped('id'):
                    order.write({'partner_shipping_id': partner_id.id})
                    complete_address = ''
                    if order.partner_shipping_id.name:
                        complete_address += order.partner_shipping_id.name
                        if any([order.partner_shipping_id.comp_name, order.partner_shipping_id.street, order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip, order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.comp_name: 
                        complete_address += order.partner_shipping_id.comp_name
                        if any([order.partner_shipping_id.street, order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.street: 
                        complete_address += order.partner_shipping_id.street
                        if any([order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.street2: 
                        complete_address += order.partner_shipping_id.street2
                        if any([order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.city and order.partner_shipping_id.state_id and order.partner_shipping_id.zip : 
                        complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.state_id.code + ' ' + order.partner_shipping_id.zip
                        if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.city and order.partner_shipping_id.state_id and not order.partner_shipping_id.zip : 
                        complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.state_id.code
                        if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.city and order.partner_shipping_id.zip and not order.partner_shipping_id.state_id : 
                        complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.zip
                        if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.state_id and order.partner_shipping_id.zip and not order.partner_shipping_id.city : 
                        complete_address += order.partner_shipping_id.state_id.code + ' ' + order.partner_shipping_id.zip
                        if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.city and not order.partner_shipping_id.state_id and not order.partner_shipping_id.zip: 
                        complete_address += order.partner_shipping_id.city
                        if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.state_id and not order.partner_shipping_id.city and not order.partner_shipping_id.zip: 
                        complete_address += order.partner_shipping_id.state_id.code
                        if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.zip and not order.partner_shipping_id.city and not order.partner_shipping_id.state_id: 
                        complete_address += order.partner_shipping_id.zip
                        if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                            complete_address += '\n'
                    if order.partner_shipping_id.country_id:
                        complete_address += order.partner_shipping_id.country_id.name 
                    order.write({'partner_ship_addr1': complete_address})
                    if default_address:
                        default_address[0].sudo().write(
                            {'default_address': False})
                else:
                    default_address = [shipping for shipping in shippings if shipping.default_address == True]
                    if default_address:
                        order.write({'partner_shipping_id': kw.get('partner_id') or default_address[0].id})
                        complete_address = ''
                        if order.partner_shipping_id.name:
                            complete_address += order.partner_shipping_id.name
                            if any([order.partner_shipping_id.comp_name, order.partner_shipping_id.street, order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip, order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.comp_name: 
                            complete_address += order.partner_shipping_id.comp_name
                            if any([order.partner_shipping_id.street, order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.street: 
                            complete_address += order.partner_shipping_id.street
                            if any([order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.street2: 
                            complete_address += order.partner_shipping_id.street2
                            if any([order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.city and order.partner_shipping_id.state_id and order.partner_shipping_id.zip : 
                            complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.state_id.code + ' ' + order.partner_shipping_id.zip
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.city and order.partner_shipping_id.state_id and not order.partner_shipping_id.zip : 
                            complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.state_id.code
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.city and order.partner_shipping_id.zip and not order.partner_shipping_id.state_id : 
                            complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.zip
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.state_id and order.partner_shipping_id.zip and not order.partner_shipping_id.city : 
                            complete_address += order.partner_shipping_id.state_id.code + ' ' + order.partner_shipping_id.zip
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.city and not order.partner_shipping_id.state_id and not order.partner_shipping_id.zip: 
                            complete_address += order.partner_shipping_id.city
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.state_id and not order.partner_shipping_id.city and not order.partner_shipping_id.zip: 
                            complete_address += order.partner_shipping_id.state_id.code
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.zip and not order.partner_shipping_id.city and not order.partner_shipping_id.state_id: 
                            complete_address += order.partner_shipping_id.zip
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.country_id:
                            complete_address += order.partner_shipping_id.country_id.name 
                        order.write({'partner_ship_addr1': complete_address})
                    else:
                        order.write({'partner_shipping_id': shippings[0].id})
                        complete_address = ''
                        if order.partner_shipping_id.name:
                            complete_address += order.partner_shipping_id.name
                            if any([order.partner_shipping_id.comp_name, order.partner_shipping_id.street, order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip, order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.comp_name: 
                            complete_address += order.partner_shipping_id.comp_name
                            if any([order.partner_shipping_id.street, order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.street: 
                            complete_address += order.partner_shipping_id.street
                            if any([order.partner_shipping_id.street2, order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.street2: 
                            complete_address += order.partner_shipping_id.street2
                            if any([order.partner_shipping_id.city, order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.city and order.partner_shipping_id.state_id and order.partner_shipping_id.zip : 
                            complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.state_id.code + ' ' + order.partner_shipping_id.zip
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.city and order.partner_shipping_id.state_id and not order.partner_shipping_id.zip : 
                            complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.state_id.code
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.city and order.partner_shipping_id.zip and not order.partner_shipping_id.state_id : 
                            complete_address += order.partner_shipping_id.city + ' ' + order.partner_shipping_id.zip
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.state_id and order.partner_shipping_id.zip and not order.partner_shipping_id.city : 
                            complete_address += order.partner_shipping_id.state_id.code + ' ' + order.partner_shipping_id.zip
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.city and not order.partner_shipping_id.state_id and not order.partner_shipping_id.zip: 
                            complete_address += order.partner_shipping_id.city
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.state_id and not order.partner_shipping_id.city and not order.partner_shipping_id.zip: 
                            complete_address += order.partner_shipping_id.state_id.code
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.zip and not order.partner_shipping_id.city and not order.partner_shipping_id.state_id: 
                            complete_address += order.partner_shipping_id.zip
                            if any([order.partner_shipping_id.state_id, order.partner_shipping_id.zip ,order.partner_shipping_id.phone, order.partner_shipping_id.country_id]):
                                complete_address += '\n'
                        if order.partner_shipping_id.country_id:
                            complete_address += order.partner_shipping_id.country_id.name 
                        order.write({'partner_ship_addr1': complete_address})
            if billings:
                default_address = [
                    billing for billing in billings if billing.default_address == True and billing != partner_id]
                if partner_id and partner_id.id in billings.mapped('id'):
                    if default_address:
                        default_address[0].sudo().write(
                            {'default_address': False})
                    order.write({'partner_invoice_id': partner_id.id})
                    complete_address = ''
                    if order.partner_invoice_id.name:
                        complete_address += order.partner_invoice_id.name
                        if any([order.partner_invoice_id.comp_name, order.partner_invoice_id.street, order.partner_invoice_id.street2, order.partner_invoice_id.city, order.partner_invoice_id.state_id, order.partner_invoice_id.zip, order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.comp_name: 
                        complete_address += order.partner_invoice_id.comp_name
                        if any([order.partner_invoice_id.street, order.partner_invoice_id.street2, order.partner_invoice_id.city, order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.street: 
                        complete_address += order.partner_invoice_id.street
                        if any([order.partner_invoice_id.street2, order.partner_invoice_id.city, order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.street2: 
                        complete_address += order.partner_invoice_id.street2
                        if any([order.partner_invoice_id.city, order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.city and order.partner_invoice_id.state_id and order.partner_invoice_id.zip : 
                        complete_address += order.partner_invoice_id.city + ' ' + order.partner_invoice_id.state_id.code + ' ' + order.partner_invoice_id.zip
                        if any([order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.city and order.partner_invoice_id.state_id and not order.partner_invoice_id.zip : 
                        complete_address += order.partner_invoice_id.city + ' ' + order.partner_invoice_id.state_id.code
                        if any([order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.city and order.partner_invoice_id.zip and not order.partner_invoice_id.state_id : 
                        complete_address += order.partner_invoice_id.city + ' ' + order.partner_invoice_id.zip
                        if any([order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.state_id and order.partner_invoice_id.zip and not order.partner_invoice_id.city : 
                        complete_address += order.partner_invoice_id.state_id.code + ' ' + order.partner_invoice_id.zip
                        if any([order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.city and not order.partner_invoice_id.state_id and not order.partner_invoice_id.zip: 
                        complete_address += order.partner_invoice_id.city
                        if any([order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.state_id and not order.partner_invoice_id.city and not order.partner_invoice_id.zip: 
                        complete_address += order.partner_invoice_id.state_id.code
                        if any([order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.zip and not order.partner_invoice_id.city and not order.partner_invoice_id.state_id: 
                        complete_address += order.partner_invoice_id.zip
                        if any([order.partner_invoice_id.state_id, order.partner_invoice_id.zip ,order.partner_invoice_id.phone, order.partner_invoice_id.country_id]):
                            complete_address += '\n'
                    if order.partner_invoice_id.country_id:
                        complete_address += order.partner_invoice_id.country_id.name 
                    order.write({'partner_invoice_addr1': complete_address})
                else:
                    if default_address:
                        order.write({'partner_invoice_id': default_address[0].id})
                    else:
                        if shippings:
                            order.write({'partner_invoice_id': shippings[0].id})
            if contacts:
                default_address = [
                    contact for contact in contacts if contact.default_address == True and contact != partner_id]
                if partner_id and partner_id.id in contacts.mapped('id'):
                    order.write({'partner_contact_id': partner_id.id})
                    string_data=""
                    complete_address = ''
                    if order.partner_contact_id.name:
                        complete_address += order.partner_contact_id.name
                        if any([order.partner_contact_id.comp_name, order.partner_contact_id.street, order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip, order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.comp_name: 
                        complete_address += order.partner_contact_id.comp_name
                        if any([order.partner_contact_id.street, order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.street: 
                        complete_address += order.partner_contact_id.street
                        if any([order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.street2: 
                        complete_address += order.partner_contact_id.street2
                        if any([order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.city and order.partner_contact_id.state_id and order.partner_contact_id.zip : 
                        complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.state_id.code + ' ' + order.partner_contact_id.zip
                        if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.city and order.partner_contact_id.state_id and not order.partner_contact_id.zip : 
                        complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.state_id.code
                        if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.city and order.partner_contact_id.zip and not order.partner_contact_id.state_id : 
                        complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.zip
                        if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.state_id and order.partner_contact_id.zip and not order.partner_contact_id.city : 
                        complete_address += order.partner_contact_id.state_id.code + ' ' + order.partner_contact_id.zip
                        if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.city and not order.partner_contact_id.state_id and not order.partner_contact_id.zip: 
                        complete_address += order.partner_contact_id.city
                        if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.state_id and not order.partner_contact_id.city and not order.partner_contact_id.zip: 
                        complete_address += order.partner_contact_id.state_id.code
                        if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.zip and not order.partner_contact_id.city and not order.partner_contact_id.state_id: 
                        complete_address += order.partner_contact_id.zip
                        if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                            complete_address += '\n'
                    if order.partner_contact_id.country_id:
                        complete_address += order.partner_contact_id.country_id.name
                    order.write({'partner_contact_phone': complete_address})
                    if default_address:
                        default_address[0].sudo().write(
                            {'default_address': False})
                else:
                    if default_address:
                        order.write({'partner_contact_id': default_address[0].id})
                        complete_address = ''
                        if order.partner_contact_id.name:
                            complete_address += order.partner_contact_id.name
                            if any([order.partner_contact_id.comp_name, order.partner_contact_id.street, order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip, order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.comp_name: 
                            complete_address += order.partner_contact_id.comp_name
                            if any([order.partner_contact_id.street, order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.street: 
                            complete_address += order.partner_contact_id.street
                            if any([order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.street2: 
                            complete_address += order.partner_contact_id.street2
                            if any([order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.city and order.partner_contact_id.state_id and order.partner_contact_id.zip : 
                            complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.state_id.code + ' ' + order.partner_contact_id.zip
                            if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.city and order.partner_contact_id.state_id and not order.partner_contact_id.zip : 
                            complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.state_id.code
                            if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.city and order.partner_contact_id.zip and not order.partner_contact_id.state_id : 
                            complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.zip
                            if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.state_id and order.partner_contact_id.zip and not order.partner_contact_id.city : 
                            complete_address += order.partner_contact_id.state_id.code + ' ' + order.partner_contact_id.zip
                            if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.city and not order.partner_contact_id.state_id and not order.partner_contact_id.zip: 
                            complete_address += order.partner_contact_id.city
                            if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.state_id and not order.partner_contact_id.city and not order.partner_contact_id.zip: 
                            complete_address += order.partner_contact_id.state_id.code
                            if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.zip and not order.partner_contact_id.city and not order.partner_contact_id.state_id: 
                            complete_address += order.partner_contact_id.zip
                            if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                complete_address += '\n'
                        if order.partner_contact_id.country_id:
                            complete_address += order.partner_contact_id.country_id.name
                        order.write({'partner_contact_phone': complete_address})
                    else:
                        if shippings:
                            order.write({'partner_contact_id': shippings[0].id})
                            complete_address = ''
                            if order.partner_contact_id.name:
                                complete_address += order.partner_contact_id.name
                                if any([order.partner_contact_id.comp_name, order.partner_contact_id.street, order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip, order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.comp_name: 
                                complete_address += order.partner_contact_id.comp_name
                                if any([order.partner_contact_id.street, order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.street: 
                                complete_address += order.partner_contact_id.street
                                if any([order.partner_contact_id.street2, order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.street2: 
                                complete_address += order.partner_contact_id.street2
                                if any([order.partner_contact_id.city, order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.city and order.partner_contact_id.state_id and order.partner_contact_id.zip : 
                                complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.state_id.code + ' ' + order.partner_contact_id.zip
                                if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.city and order.partner_contact_id.state_id and not order.partner_contact_id.zip : 
                                complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.state_id.code
                                if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.city and order.partner_contact_id.zip and not order.partner_contact_id.state_id : 
                                complete_address += order.partner_contact_id.city + ' ' + order.partner_contact_id.zip
                                if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.state_id and order.partner_contact_id.zip and not order.partner_contact_id.city : 
                                complete_address += order.partner_contact_id.state_id.code + ' ' + order.partner_contact_id.zip
                                if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.city and not order.partner_contact_id.state_id and not order.partner_contact_id.zip: 
                                complete_address += order.partner_contact_id.city
                                if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.state_id and not order.partner_contact_id.city and not order.partner_contact_id.zip: 
                                complete_address += order.partner_contact_id.state_id.code
                                if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.zip and not order.partner_contact_id.city and not order.partner_contact_id.state_id: 
                                complete_address += order.partner_contact_id.zip
                                if any([order.partner_contact_id.state_id, order.partner_contact_id.zip ,order.partner_contact_id.phone, order.partner_contact_id.country_id]):
                                    complete_address += '\n'
                            if order.partner_contact_id.country_id:
                                complete_address += order.partner_contact_id.country_id.name
                            order.write({'partner_contact_phone': complete_address})
            values = {
                'order': order,
                'shippings': shippings,
                'billings': billings,
                'contacts': contacts,
                'only_services': order and order.only_services or False
            }
        return values

    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values = {}
        authorized_fields = request.env['ir.model'].sudo().search(
            [('model', '=', 'res.partner')])._get_form_writable_fields()
        for k, v in values.items():
            # don't drop empty value, it could be a field to reset
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:  # DEBUG ONLY
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'):  # classic case
                    _logger.debug(
                        "website_sale postprocess: %s value has been dropped (empty or not writable)" % k)

        if new_values.get('default_address'):
            new_values['default_address'] = True
        else:
            new_values['default_address'] = False
        if new_values.get('use_acc_comm'):
            new_values['use_acc_comm'] = True
        else:
            new_values['use_acc_comm'] = False
        new_values['customer'] = True
        new_values[
            'team_id'] = request.website.salesteam_id and request.website.salesteam_id.id

        lang = request.lang if request.lang in request.website.mapped(
            'language_ids.code') else None
        if lang:
            new_values['lang'] = lang
        parent_id = order.partner_id.commercial_partner_id.id
        if mode[1] == 'contact':
            new_values['type_extend'] = 'contact'
            if mode[0] == 'new':
                new_values['parent_id'] = parent_id

        if mode[1] == 'billing':
            new_values['type_extend'] = 'invoice'
            if mode[0] == 'new':
                new_values['parent_id'] = parent_id

        if mode[1] == 'shipping':
            new_values['type_extend'] = 'delivery'
            new_values['type'] = 'delivery'
            if mode[0] == 'new':
                new_values['parent_id'] = parent_id

        return new_values, errors, error_msg

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):

        # if not kw.get('mode'):
        #     return request.redirect('/shop/checkout')

        mode1 = kw.get('mode', False)
        communication_phone_type = request.env[
            'communication.type'].sudo().search([('for_phone', '=', True)])
        communication_other_type = request.env[
            'communication.type'].sudo().search([('for_other', '=', True)])
        country_selected = request.env[
            'res.country'].sudo().search([('code', '=', 'US')])
        Partner = request.env['res.partner'].with_context(
            show_address=1).sudo()
        order = request.website.sale_get_order()

        mode = (False, False)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search(
                    [('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'account')
                else:
                    if mode1:
                        if mode1 == 'billing':
                            mode = ('edit', 'billing')
                        elif mode1 == 'contact':
                            mode = ('edit', 'contact')
                        elif mode1 == 'shipping':
                            mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                if mode1:
                    if mode1 == 'billing':
                        mode = ('new', 'billing')
                    elif mode1 == 'contact':
                        mode = ('new', 'contact')
                    elif mode1 == 'shipping':
                        mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(
                mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(
                order, mode, pre_values, errors, error_msg)
            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                post['supplier'] = False
                post['customer'] = False
                partner_id = self._checkout_form_save(mode, post, kw)
                # order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/checkout')
        country = 'country_id' in values and values['country_id'] != '' and request.env[
            'res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'country_selected': country_selected,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'communication_phone_type': communication_phone_type,
            'communication_other_type': communication_other_type,
            'callback': kw.get('callback'),
        }
        return request.render("website_sale.address", render_values)

    @http.route(['/get-contact-info'], type='json', auth="public", methods=['POST'])
    def get_contact_info(self, **kw):

        partner_id = request.env.user.partner_id
        vals = {
            'name': partner_id.name or '',
            'company': partner_id.company_id.name or '',
            'street': partner_id.street or '',
            'street2': partner_id.street2 or '',
            'city': partner_id.city or '',
            'state_id': partner_id.state_id.id or '',
            'state': partner_id.state_id.name or '',
            'zip': partner_id.zip or '',
            'country_id': partner_id.country_id.id or '',
            'country': partner_id.country_id.name or '',
            'email': partner_id.email or '',
            'phone': partner_id.phone or '',
            'primary_tel_type': partner_id.primary_tel_type.id or '',
            'other_communication_1': partner_id.alternate_communication_1 or '',
            'other_communication_type_1': partner_id.alternate_commu_type_1.id or '',
            'other_communication_2': partner_id.alternate_communication_2 or '',
            'other_communication_type_2': partner_id.alternate_commu_type_2.id or '',
        }
        return vals

    def checkout_redirection(self, order):
        # must have a draft sales order with lines at this point, otherwise reset
        if not order or order.state != 'draft':
            request.session['sale_order_id'] = None
            request.session['sale_transaction_id'] = None
            return request.redirect('/shop')

        # if transaction pending / done: redirect to confirmation
        tx = request.env.context.get('website_sale_transaction')
        if tx and tx.state != 'draft':
            return request.redirect('/shop/payment/confirmation/%s' % order.id)
