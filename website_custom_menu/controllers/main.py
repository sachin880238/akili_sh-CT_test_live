# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request


class WebsiteHeaderButtonPopOver(http.Controller):

    @http.route(['/get/popover'], type='http', auth="public", website=True)
    def get_pop_over(self, **post):

        if post.get('type') == 'call-popover':
            return request.render("website_custom_menu.call_popover")

        if post.get('type') == 'login-popover':
            return request.render("website_custom_menu.login_popover")

        if post.get('type') == 'email-popover':
            return request.render("website_custom_menu.email_popover")
