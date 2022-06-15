# -*- coding: utf-8 -*-
import os
from odoo import api, fields, models


class Website(models.Model):
    _inherit = "website"

    svg_colour = fields.Char("SVG Colour")


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    def _default_website(self):
        return self.env['website'].search([], limit=1)

    website_id = fields.Many2one(
        'website', string="website", default=_default_website, required=True)
    svg_colour = fields.Char(related="website_id.svg_colour", string="SVG Colour")


    def change_svg_colour(self):
        current_path = os.getcwd()
        file_path = '/website_custom_menu/static/src/img/svg/EmailButton.svg'

class override_menu(models.Model):
    _inherit = "website.menu"

    @api.model
    def get_tree(self, website_id, menu_id=None):
        def make_tree(node):
            page_id = node.page_id.id if node.page_id else None
            is_homepage = page_id and self.env['website'].browse(website_id).homepage_id.id == page_id
            menu_node = dict(
                id=node.id,
                name=node.name,
                url=node.page_id.url if page_id else node.url,
                new_window=node.new_window,
                sequence=node.sequence,
                parent_id=node.parent_id.id,
                children=[],
                is_homepage=is_homepage,
            )
            for child in node.child_id:
                if not child.website_product_catag_id:
                    menu_node['children'].append(make_tree(child))
            return menu_node
        if menu_id:
            menu = self.browse(menu_id)
        else:
            menu = self.env['website'].browse(website_id).menu_id
        return make_tree(menu)