# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Product(models.Model):
    _inherit = "product.template"

    cur_symbol = fields.Char(
        related="currency_id.symbol", string='Currency Symbol')


class ProductProduct(models.Model):

    _inherit = 'product.product'

    public_categ_ids = fields.Many2many('product.public.category', string='Website Product Category',
                                        help="Categories can be published on the Shop page (online catalog grid) to help "
                                        "customers find all the items within a category. To publish them, go to the Shop page, "
                                        "hit Customize and turn *Product Categories* on. A product can belong to several categories.")
    

    @api.multi
    def get_display_name(self):
        default_code = '[%s]'%(self.default_code) if self.default_code else ''
        product_name = self.website_name or self.name
        attr_vals = '(%s)'%(self.attr_vals[2:]) if self.attr_vals else ''

        return (default_code + product_name + attr_vals)


class Website(models.Model):
    _inherit = "website"

    ppp_on_find = fields.Selection([('2', '2'), ('5', '5'),('10', '10'), ('25', '25'), ('50', '50'), (
        'all', 'All')], string="Products per page on the page of find a product.", default="10")



class WebsiteConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    def _default_website(self):
        return self.env['website'].search([], limit=1)

    website_id = fields.Many2one(
        'website', string="website", default=_default_website, required=True)
    ppp_on_find = fields.Selection(related="website_id.ppp_on_find", string="Products Per Page", readonly=False)
