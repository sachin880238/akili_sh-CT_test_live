import datetime
import json
import urllib
import werkzeug

from odoo import http, SUPERUSER_ID
from odoo.http import request


class Confirm_order_custom(http.Controller):

	@http.route(['/shop/confirm_order_custom'], type='http', methods=['GET', 'POST'], auth="public", website=True)
	def ConfirmOrderCustom(self, **kw):
		order = request.website.sale_get_order()
		request.session['sale_order_id'] = None
		render_values = {
		 'website_sale_order' : order,
		}
		return request.render("custom_web_checkout.confirm_order_custom",render_values)
