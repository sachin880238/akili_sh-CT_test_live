from odoo import http, tools, _, fields
import datetime
import json
import urllib
import werkzeug
from odoo import http, SUPERUSER_ID
from odoo.http import request



class ReviewPage(http.Controller):


	# extra information page
	@http.route(['/shop/review'], type='http', methods=['GET', 'POST'], auth="public", website=True)
	def review_page(self, **kw):
		order = request.website.sale_get_order()
		if not order:
			return request.render('website.404')
		error = False
		attchments = request.env['ir.attachment'].search([('res_model','=', 'sale.order'),('res_id','=',order.id)])
		if 'submitted' in  kw:
			order.sudo().write({'sent_cart': True, 'validity_date':fields.Date.today(), 'cart_state': 'rfq'})
			return request.redirect('/shop/confirm_order_custom')
		render_values = {
		'website_sale_order' : order,
		'order_attachments': attchments,
		'error' : error
		}
		return request.render("custom_web_checkout.review_page",render_values)