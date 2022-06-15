# -*- coding: utf-8 -*-
from odoo import http, tools, _, fields
from odoo.http import content_disposition, Controller, request, route
import datetime
import base64
# from odoo.exceptions import AccessError
from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.mail import _message_post_helper
# from odoo.addons.ct_web_checkout.controllers.main import ProductRedirect

class CustomerPortalExtends(CustomerPortal):

    @http.route(['/my/carts', '/my/carts/page/<int:page>'], type='http', auth="public", website=True)
    def get_my_carts(self, page=1, date_begin=None, date_end=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order'].sudo()

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('is_cart_saved', '=', True),
            ('state', 'in', ['draft']),
            ('sent_cart', '=', False),
        ]
        if post.get('expire'):
            if post.get('expire') == 'yes':
                domain += [('validity_date', '<', fields.Date.today())]
            else:
                domain += [('validity_date', '>=', fields.Date.today())]

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        saved_cart_count = SaleOrder.sudo().search_count(domain)

        pager = request.website.pager(
            url="/my/carts",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=saved_cart_count,
            page=page,
            step=self._items_per_page
        )

        # search the count to display, according to the pager data
        quotations = SaleOrder.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'quotations': quotations,
            'pager': pager,
            'default_url': '/my/carts',
        })
        return request.render("website_my_account.portal_my_saved_carts", values)


    @http.route(['/my/carts/<int:order>'], type='http', auth="user", website=True)
    def orders_saved_cart(self, order=None, **kw):
        order = request.env['sale.order'].sudo().browse([order])
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            return request.render("website.403")

        order_sudo = order.sudo()
        order_invoice_lines = {il.product_id.id: il.invoice_id for il in order_sudo.invoice_ids.mapped('invoice_line_ids')}

        vals = {
            'order': order_sudo,
            'order_invoice_lines': order_invoice_lines,
        }
        if kw.get('warning'):
            vals['warning'] = kw.get('warning')
        
        return request.render("website_my_account.orders_saved_cart", vals)

    # activate cart from save cart    
    @http.route(['/cart/activate/<int:order>'], type='http', auth="user", website=True)
    def saved_cart_activate(self, order=None, **kw):
        partner = request.env.user.partner_id
        if partner.last_website_so_id:
            if partner.last_website_so_id.order_line:
                return request.redirect("/my/carts/%s?warning=Please process the pending active order first" % order)
            else:
                partner.last_website_so_id.unlink()
        request.session['sale_order_id'] = order
        sale_order = request.env['sale.order'].browse([order])
        sale_order.sudo().write({'is_cart_saved': False, 'cart_state': 'active'})
        pricelist=request.env.user.partner_id.property_product_pricelist
        for rec in sale_order.order_line:
            rec.compute_price_for_website()
        return request.redirect('/shop/cart')



    @http.route(['/delete_saved/cart'], type='json', auth="user", methods=['POST'])
    def configure_delete_saved_cart(self,  **kw):
        saved_cart_id=kw.get('saved_cart_id')
        save_obj = request.env['sale.order']
        saved_carts = save_obj.sudo().search(
            [('id', '=', saved_cart_id)])
        saved_carts.unlink()

        return kw


    @http.route(['/my/sent_carts', '/my/sent_carts/page/<int:page>'], type='http', auth="public", website=True)
    def get_my_sent_cart(self, page=1, date_begin=None, date_end=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order'].sudo()

        # remove sent cart field from domain bcz comes from so_do_workflow module
        # domain = [
        #     ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        #     ('state', 'in', ['draft', 'cancel']),
        # ]

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft', 'cancel']),
            ('sent_cart', '=', True),
        ]

        if post.get('expire'):
            if post.get('expire') == 'yes':
                domain.append(('validity_date', '<', fields.Date.today()))
            else:
                domain.append(('validity_date', '>=', fields.Date.today()))
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        saved_cart_count = SaleOrder.sudo().search_count(domain)

        pager = request.website.pager(
            url="/my/carts",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=saved_cart_count,
            page=page,
            step=self._items_per_page
        )

        # search the count to display, according to the pager data
        quotations = SaleOrder.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'quotations': quotations,
            'pager': pager,
            'default_url': '/my/sent_cart',
            'website': request.website
        })
        return request.render("website_my_account.portal_my_sent_carts", values)


    @http.route(['/my/sent-carts/<int:order>'], type='http', auth="user", website=True)
    def orders_sent_cart(self, order=None, **kw):

        order = request.env['sale.order'].sudo().browse([order])
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            return request.render("website.403")

        order_sudo = order.sudo()
        order_invoice_lines = {il.product_id.id: il.invoice_id for il in order_sudo.invoice_ids.mapped('invoice_line_ids')}

        if kw.get('action'):
            if kw.get('action') == 'activate':
                order_sudo.action_draft()
            if kw.get('action') == 'cancel':
                order_sudo.action_cancel()
        vals = {
            'order': order_sudo,
            'order_invoice_lines': order_invoice_lines,
        }
        return request.render("website_my_account.orders_sent_cart", vals)



    @http.route(['/my/quotes/', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order'].sudo()
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('is_cart_saved', '=', False),
            ('sent_cart', '=', False),
            ('state', 'in', ['cancel','sent','order']),
        ]
        if kw.get('expire'):
            if kw.get('expire') == 'yes':
                domain.append(('validity_date', '<', fields.Date.today()))
            else:
                domain.append(('validity_date', '>=', fields.Date.today()))

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.sudo().search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'quotations': quotations,
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
        })
        return request.render("website_my_account.custom_portal_my_quotations", values)


    #@http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    #def portal_my_orders(self, page=1, date_begin=None, date_end=None, **kw):
    #    res= super(CustomerPortalExtends, self).portal_my_orders(page=page, date_begin=date_begin, date_end=date_end,kw=kw)
    #    values = res.qcontext
    #    filter_order = []
    #    for order in  values.get('orders'):
    #        if kw.get('state') == 'sale':
    #            if order.state == 'sale':
    #                filter_order.append(order.id)
    #        else:
    #            if order.state == 'done':
    #               filter_order.append(order.id)
    #    if filter_order:
    #        values['orders'] =  request.env['sale.order'].browse(filter_order)
    #    return request.render("website_my_account.custom_portal_my_orders", values)


    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, **kw):
        res= super(CustomerPortalExtends, self).portal_my_invoices(page=page, date_begin=date_begin, date_end=date_end,kw=kw)
        values = res.qcontext
        filter_invoice = []
        if kw.get('state'):
            for invoice in  values.get('invoices'):
                if kw.get('state') == 'not_paid':
                    if invoice.state != 'paid':
                        filter_invoice.append(invoice.id)
                else:
                    if invoice.state == 'paid':
                        filter_invoice.append(invoice.id)
        if filter_invoice:
            values['invoices'] =  request.env['account.invoice'].browse(filter_invoice)
        return request.render("website_my_account.custom_portal_my_invoices", values)


    @http.route(['/my/statement'], type='http', auth="user", website=True)
    def partner_statment(self, page=1, date_begin=None, date_end=None, **kw):
        # Below code commented bcz account_repots has no table account partner ledger context but 10 has so comment


        # partner = request.env.user.partner_id
        # context_id = request.env['account.partner.ledger.context'].sudo().create({})
        # account_types = []
        # if 'receivable' in context_id.account_type:
        #     account_types.append('receivable')
        # if 'payable' in context_id.account_type:
        #     account_types.append('payable')
        # new_context = {
        #     'date_from': context_id.date_from,
        #     'date_to': context_id.date_to,
        #     'state': context_id.all_entries and 'all' or 'posted',
        #     'cash_basis': context_id.cash_basis,
        #     'context_id': context_id,
        #     'company_ids': context_id.company_ids.ids,
        #     'account_types': account_types
        # }
        # data = request.env['account.partner.ledger'].sudo().with_context(new_context)._lines_partner(partner)
        # values = {
        #     'statments': (data and data[0]['columns'][-1]),
        #     'due_balance' : (data and data[0]['columns'][-2])
        #     }
        values = {
            'statments': False,
            'due_balance' : False
        }
        return request.render("website_my_account.custom_portal_my_statement", values)


    # @http.route(['/my/orders/<int:order_id>',], type='http', auth='public', website=True)
    # def portal_order_page(self, order_id=None, **):

    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        res= super(CustomerPortalExtends, self).portal_order_page(order_id=order_id, report_type=report_type, access_token=access_token, message=message, download=download, kw=kw)
        values = res.qcontext
        if values.get('sale_order'):
            order = values.get('sale_order')
            if order.validity_date and order.validity_date > fields.Date.today() and order.quote_stage == 'accept' and not order.is_portal_authorised:
                values.update({'purchase':True})
            if order.quote_stage not in ['accept', 'order']:
                values.update({'to_review':True})
            if order.is_portal_authorised:
                values.update({'order_pending':True})         
            if order.is_cart_saved:
                values.update({'order_type': "saved_cart"})
            elif order.sent_cart:
                values.update({'order_type': "sent_cart"})
                return request.render("website_my_account.custom_orders_followup", values)
            elif order.state in  ['sent','cancel']:
                values.update({'order_type': "quotation"})
            else:
                values.update({'order_type': "order"})
            return request.render("website_my_account.custom_orders_followup", values)
        else:
            return res


    @http.route(['/my/invoices/<int:invoice>'], type='http', auth="user", website=True)
    def invoices_followup(self, invoice=None, **kw):
        invoice = request.env['account.invoice'].sudo().browse([invoice])
        try:
            invoice.check_access_rights('read')
            invoice.check_access_rule('read')
        except AccessError:
            return request.render("website.403")

        invoice_sudo = invoice.sudo()

        vals =  {
            'invoice': invoice_sudo,
        }

        return request.render("website_my_account.custom_invoices_followup", vals)


    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        res = super(CustomerPortalExtends, self).home(kw=kw)
        values = res.qcontext

        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order'].sudo()
        AccountInvoice = request.env['account.invoice'].sudo()
        Helpdesk_stage = request.env['helpdesk_lite.stage'].sudo()
        Helpdesk_ticket = request.env['helpdesk_lite.ticket'].sudo()
        partner = request.env.user.partner_id

        # is_cart_saved found in so_do_worklfow module
        # sent_cart found in so_do_worklfow module
        # saved_cart = SaleOrder.sudo().search([])
        saved_cart = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft']),
            ('is_cart_saved', '=', True),
            ('sent_cart', '=', False),
            ('validity_date', '>=', fields.Date.today())
        ])

        # saved_cart_expire = SaleOrder.sudo().search([])
        saved_cart_expire = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft']),
            ('is_cart_saved', '=', True),
            ('sent_cart', '=', False),
            ('validity_date', '<', fields.Date.today())
        ])

        # rfq_cart = SaleOrder.sudo().search([])
        rfq_cart = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sent_cart', '=', True),
            ('state', 'in', ['draft', 'cancel']),
            ('validity_date', '>=', fields.Date.today())
        ])

        # rfq_cart_expire = SaleOrder.sudo().search([])
        rfq_cart_expire = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sent_cart', '=', True),
            ('state', 'in', ['draft', 'cancel', 'sent']),
            ('validity_date', '<', fields.Date.today())
        ])
        # quotation = SaleOrder.sudo().search([])
        quotation = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['cancel','sent']),
            ('is_cart_saved', '=', False),
            ('sent_cart', '=', False),
            ('validity_date', '>=', fields.Date.today())
        ])

        # quotation_expire = SaleOrder.sudo().search([])
        quotation_expire = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['cancel', 'sent']),
            ('is_cart_saved', '=', False),
            ('sent_cart', '=', False),
            ('validity_date', '<', fields.Date.today())
        ])


        order_sale = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'sale')
        ])

        order_done = SaleOrder.search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['done'])
        ])


        invoice_paid = AccountInvoice.search([
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['paid'])
        ])

        invoice_not_paid = AccountInvoice.search([
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'not in', ['paid'])
        ])

        stage_inprogress = Helpdesk_stage.sudo().search([
            '|', ('sequence', '=', 0), ('sequence', '=', 1)
        ])

        stage_solved = Helpdesk_stage.sudo().search([
            ('sequence', 'in', [2,3])
        ])


        customer_service_ticket = Helpdesk_ticket.sudo().search([
            ('stage_id', 'in', stage_inprogress.ids),
            ('partner_id', '=', partner.id)

        ])

        customer_service_ticket_solved = Helpdesk_ticket.sudo().search([
            ('stage_id', 'in', stage_solved.ids),
            ('partner_id', '=', partner.id)
        ])

        values.update({
            'saved_cart': saved_cart,
            'saved_cart_expire': saved_cart_expire,
            'saved_cart_count': len(saved_cart),
            'saved_cart_expire_count': len(saved_cart_expire),
            'rfq_cart': rfq_cart,
            'rfq_cart_expire': rfq_cart_expire,
            'rfq_cart_count': len(rfq_cart),
            'rfq_cart_expire_count': len(rfq_cart_expire),
            'quotation': quotation,
            'quotation_expire': quotation_expire,
            'quotation_count': len(quotation),
            'quotation_expire_count': len(quotation_expire),
            'order_sale': order_sale,
            'order_done': order_done,
            'order_sale_count': len(order_sale),
            'order_done_count': len(order_done),
            'invoice_paid': invoice_paid,
            'invoice_not_paid' : invoice_not_paid,
            'invoice_paid_count': len(invoice_paid),
            'invoice_not_paid_count' : len(invoice_not_paid),
            'customer_service_ticket': customer_service_ticket,
            'customer_service_ticket_solved': customer_service_ticket_solved,
            'customer_service_ticket_count': len(customer_service_ticket),
            'customer_service_ticket_solved_count': len(customer_service_ticket_solved),

        })

        return request.render("website_my_account.custom_portal_my_home", values)

    @http.route(['/my/ticket'], type='http', auth="user", website=True)
    def customer_ticket(self, **kw):
        Helpdesk_stage = request.env['helpdesk.stage']
        stage_inprogress = Helpdesk_stage.sudo().search([
            '|', ('sequence', '=', 0), ('sequence', '=', 1)
        ])

        stage_solved = Helpdesk_stage.sudo().search([
            ('sequence', 'in', [2,3])
        ])

        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id)]
        # domain = [('message_partner_ids', 'child_of', [partner.commercial_partner_id.id])]
        if kw.get('state'):
            if kw.get('state') == 'not_solved':
                domain.append(('stage_id', 'in', stage_inprogress.ids))
            else:
                domain.append(('stage_id', 'in', stage_solved.ids))
        customer_ticket = request.env['helpdesk.ticket'].sudo().search(domain)
        values = {'customer_ticket': customer_ticket}
        return request.render("website_my_account.customer_support_tickets", values)

    @http.route(['/my/ticket_details/<int:ticket>'], type='http', auth="user", website=True)
    def customer_ticket_details(self, ticket=None, **kw):
        customer_ticket = request.env['helpdesk.ticket'].sudo().search([('id', '=', ticket)])
        attachments = request.env['ir.attachment'].sudo().search([('res_model','=', 'helpdesk.ticket'),('res_id','=',ticket)])
        att_obj = request.env['ir.attachment'].sudo()

        if kw.get('upload_attachment') == 'yes':
            datas = ''
            if (hasattr(kw.get('ticket_doc'),'stream')) and hasattr(kw.get('ticket_doc').stream,'getvalue'):
                datas = kw.get('ticket_doc').stream.getvalue()

            if datas:
                attachment = att_obj.sudo().create({
                    'name': customer_ticket.name,
                    'type': 'binary',
                    'datas' :  base64.encodestring(datas),
                    'res_model' : 'helpdesk.ticket',
                    'res_id': customer_ticket.id,
                    'datas_fname': kw.get('ticket_doc').filename
                })
                attachments += attachment
        values = {'customer_ticket': customer_ticket,
                   'attachments' : attachments,
                   'upload_attachment' : False
            }
        return request.render("website_my_account.customer_support_tickets_details", values)


    # Purchase Process for payment


    # @http.route(['/quote/purchase/<int:order>'], type='http', auth="user", website=True)
    # def quotation_purchase(self, order=None, **kw):
    #     credit_card_detail_obj = request.env['credit.card.detail']
    #     warning = False
    #     if kw.get('card_value_add_or_change'):
    #         values = {
    #                 'month': kw.get('month'),
    #                 'year': kw.get('year'),
    #                 'debit_card_no': kw.get('debit_card_no'),
    #                 'card_holder_name': kw.get('card_holder_name')
    #         }
    #         if kw.get('card_value_add_or_change') == 'change':
    #             credit_card_details = credit_card_detail_obj.sudo().search([
    #                 ('id', '=', kw.get('credit_card_detail_id'))])

    #             credit_card_details.sudo().write(values)

    #         if kw.get('card_value_add_or_change') == 'add':
    #             credit_card_details = credit_card_detail_obj.sudo().search([
    #                 ('debit_card_no', '=', kw.get('debit_card_no'))])
    #             if not credit_card_details:
    #                 values['partner_id'] = kw.get('partner_id_model')
    #                 credit_card_details = credit_card_detail_obj.sudo().create(values)
    #             else:
    #                 warning = 'Card Number is Already Exists'    
      
    #         if kw.get('card_value_add_or_change') == 'remove':
    #             credit_card_details = credit_card_detail_obj.sudo().search([
    #                 ('id', '=', kw.get('credit_card_detail_id'))])
    #             if credit_card_details:
    #                 credit_card_details.sudo().unlink() 
    #     order_sale = request.env['sale.order'].sudo().search([('id', '=', order)])
        
    #     for card_detail_ids in order_sale.partner_id.partner_card_detail_ids:
    #         number = 'XXX XXXX XXX '+ card_detail_ids.debit_card_no[-4:]
            

    #         setattr(card_detail_ids, 'debit_card_no_encrypt', number)
    #     values = {
    #             'order_sale': order_sale,
    #             'credit_card_details': order_sale.partner_id.partner_card_detail_ids,
    #             'warning': warning
    #         }
    #     return request.render("website_my_account.portal_purchase_approved", values)


    # @http.route(['/approve/purchase'], type='http', auth="user", website=True)
    # def approved_purchase(self, order=None, **kw):
    #     order_sale = False
    #     if kw.get('sale_order_id'):
    #         order_sale = request.env['sale.order'].sudo().search([('id', '=', kw.get('sale_order_id'))])
    #         if order_sale.signature == 'yes':
    #             values ={
    #                 'sale_order' : order_sale
    #             }
    #             return request.render("website_my_account.portal_signature", values)
    #         else:
    #             order_sale.write({'is_portal_authorised':True}) 
    #             return request.redirect('/my/orders/%s' %(order_sale.id))     

    # @http.route(['/portal/signature'], type='json', auth="user", website=True)
    # def portal_signature(self, order_id=None, token=None, sign=None, customer_name=None, **kw):
        
    #     warning = False
    #     values = False
    #     Order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
    #     attachments = [('signature.png', base64.b64decode(sign))] if sign else [] 
    #     message = _('Order signed by %s') % (customer_name)
    #     # if token != Order.access_token or Order.require_payment:
    #     #     return request.render('website.404')
    #     _message_post_helper(message=message, res_id=Order.id, res_model='sale.order', attachments=attachments, **({'token': token, 'token_field': 'access_token'} if token else {}))
    #     values = {
    #         'order_id': order_id
    #     }
    #     Order.write({'is_portal_authorised':True})   
    #     return values

    # quote reject functionality
    # @http.route(['/quote/reject'], type='json', auth="public", website=True)
    # def quote_reject(self, order_id=None,reason=None, **post):
    #     Order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
    #     Order.write({'state':'cancel'})
    #     message = _('Quotation Rejected reason is  %s') % (reason)
    #     _message_post_helper(message=message, res_id=Order.id, res_model='sale.order', **({'token': Order.access_token, 'token_field': 'access_token'} if Order.access_token else {}))
    #     values = {
    #         'order_id': order_id
    #     }    
    #     return values      


class WebsiteSaleAddressExtend(WebsiteSale):


    @http.route(['/shop/save_cart'], type='http', auth="public", methods=['POST'], website=True)
    def save_cart(self, **kw):
        if 'save_note' in kw:
            order = request.website.sale_get_order(force_create=1)
            order.write({'is_cart_saved': True, 'validity_date':fields.Date.today(), 'cart_state': 'saved', 'quote_comment': kw['save_note']})
        request.session.pop('sale_order_id')
        request.env.user.partner_id.last_website_so_id = False
        return request.redirect('/shop/cart')


    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        res= super(WebsiteSaleAddressExtend, self).address(**kw)
        if not kw.get('submitted'):
            res.qcontext['address_book'] = kw.get('address_book',False)
        else:
            if res.location:
                if kw.get('address_book'):
                    res.location = '/my/address-book'
        return res

    @http.route(['/my/address-book'], type='http', auth="public", website=True)
    def address_book(self, **post):
        order = request.website.sale_get_order()

        values = self.checkout_values(**post)
        # Avoid useless rendering if called in ajax
        values['address_book'] = True
        return request.render("custom_web_checkout.v_checkout_inherited", values)


    @http.route(['/my/address'], type='http', auth="user", website=True)
    def account_address(self, **post):
        communication_type_ids = request.env['communication.type'].sudo().search([])
        country_ids = request.env['res.country'].search([])
        country_selected = request.env['res.country'].sudo().search([('code', '=', 'US')])
        login_with =  post.get('login_with')
        text_code =  post.get('text_code')
        security_question =  post.get('security_question')
        user = request.env.user

        if login_with == 'email_sign':
            self.is_email_auth = True
            self.is_password_auth = False
            vals = {
            'is_email_auth': self.is_email_auth,
            'is_password_auth': self.is_password_auth,
            }
            user.write(vals)


        if login_with == 'password_sign':
            self.is_password_auth = True
            self.is_email_auth = False
            vals = {
            'is_email_auth': self.is_email_auth,
            'is_password_auth': self.is_password_auth,
            }
            user.write(vals)

        vals = {
            'is_mobile_auth': text_code,
            'is_security_auth': security_question,
        }
        user.write(vals)



        values = {
            'communication_type_ids': communication_type_ids,
            'country_ids': country_ids,
            'state_ids': country_selected.state_ids,
            'partner_id': request.env.user.partner_id,
            'user_id': request.env.user,
            'kw': post
        }

        if post:
            MANDATORY_FIELDS = ['street', 'city', 'zip', 'state_id', 'country_id', 'phone', 'primary_tel_type']
            error={}
            for field_name in MANDATORY_FIELDS:
                if not post.get(field_name):
                    error[field_name] = 'Some required fields are empty!'
                    error['error_message'] = 'Some required fields are empty!'
                    values.update({
                        'error': error,
                    })

            if error:
                return request.render("website_my_account.custom_portal_my_address", values)

            partner_id = request.env.user.partner_id

            vals = {
                'street': post.get('street'),
                'street2': post.get('street2'),
                'city': post.get('city'),
                'state_id': post.get('state_id', False) and int(post.get('state_id')),
                'zip': post.get('zip'),
                'country_id': post.get('country_id', False) and int(post.get('country_id')),
                'phone': post.get('phone'),
                'primary_tel_type': post.get('primary_tel_type', False) and int(post.get('primary_tel_type')),
                'alternate_communication_1': post.get('alternate_communication_1'),
                'alternate_commu_type_1': post.get('alternate_commu_type_1', False) and int(post.get('alternate_commu_type_1')),
                'alternate_communication_2': post.get('alternate_communication_2'),
                'alternate_commu_type_2': post.get('alternate_commu_type_2', False) and int(post.get('alternate_commu_type_2')),
            }
            partner_id.write(vals)
            return request.redirect("/my/home")

        return request.render("website_my_account.custom_portal_my_address", values)

    @http.route('/country/state', csrf=False, type="json", methods=['POST'],   auth="public", website=True)
    def countrychange(self,country_id,*kw):
        temp=0

        state_details = request.env['res.country.state'].sudo().search([('country_id.id', '=', country_id)])
        state_dict={}
        for rec in state_details:
            state_dict[rec.id]=rec.name

       
        return state_dict


    @http.route(['/fetch/saved_cart/record'], type='json', auth="public", methods=['GET', 'POST'])
    def fetchsavedcartrecord(self,  **kw):
        saved_cart_id=request.env['product.product'].sudo().search([])
        # for rec in saved_cart_id:
        #     print("QWQWQW!@!@!@!@",rec.name,rec.full_name)
        # if kw['name'] == 'Website Header Icon Email Config Setting':
        #     record_id=request.env['system.config'].sudo().search([('name','=','Website Header Icon Email Config Setting')])
        #     cross_id = request.env['system.config'].sudo().search([('name','=','Website Header Color Config Setting')])
        # if kw['name'] == 'Website Header Icon Call Config Setting':
        #     record_id=request.env['system.config'].sudo().search([('name','=','Website Header Icon Call Config Setting')])
        #     cross_id = request.env['system.config'].sudo().search([('name','=','Website Header Color Config Setting')])
        
        # data={'html_data':record_id.taxt_email,
        #         'header_color':record_id.mail_header_color,
        #         'header_data':record_id.main_heading_email,
        #         'cross_color':cross_id.web_header_content_color,
        #     }

        
        return saved_cart_id    


    # @http.route(['/delete_saved/cart'], type='json', auth="user", methods=['POST'])
    # def configure_delete_saved_cart(self,  **kw):
    #     saved_cart_id=kw.get('saved_cart_id')
    #     save_obj = request.env['sale.order']
    #     saved_carts = save_obj.sudo().search(
    #         [('id', '=', saved_cart_id)])
    #     saved_carts.unlink()

    #     return kw
    

   
