# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.custom_web_checkout.controllers.extra_info import ExtraInfo
from odoo.addons.custom_web_checkout.controllers.review_page import ReviewPage


class ShopCheckOutWizard(WebsiteSale):

    @http.route()
    def checkout(self, **post):
        res = super(ShopCheckOutWizard, self).checkout(**post)
        order = request.website.sale_get_order()
        for order1 in order:
            order1.wizard_address = True
        return res


class ExtraInfoWizard(ExtraInfo):

    @http.route()
    def extra_info_custom(self, **kw):
        res = super(ExtraInfoWizard, self).extra_info_custom(**kw)
        order = request.website.sale_get_order()
        if 'submitted' in kw:
            order.wizard_reviews = True
        order.wizard_details = True
        return res


class ReviewPageWizard(ReviewPage):

    @http.route()
    def review_page(self, **kw):
        res = super(ReviewPageWizard, self).review_page(**kw)
        order = request.website.sale_get_order()
        if 'submitted' in kw:
            order.wizard_confirm = True
            order.wizard_reviews = False
            order.wizard_details = False
            order.wizard_address = False
            order.disabled_wizard = True
        return res