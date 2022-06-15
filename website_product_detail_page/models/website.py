# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


# class Website(models.Model):
#     _inherit = 'website'

    # thumbnail_panel_position = fields.Selection([
    #     ('left', 'Left'),
    #     ('right', 'Right'),
    #     ('bottom', 'Bottom'),
    # ], default='left',
    #     string='Thumbnails panel position',
    #     help="Select the position where you want to display the thumbnail panel in multi image.")
    # interval_play = fields.Char(
    #     string='Play interval of slideshow',
    #     default='5000',
    #     help='With this field you can set the interval play time between two images.')
    # enable_disable_text = fields.Boolean(
    #     string='Enable the text panel',
    #     default=True,
    #     help='Enable/Disable text which is visible on the image in multi image.')
    # color_opt_thumbnail = fields.Selection([
    #     ('default', 'Default'),
    #     ('b_n_w', 'B/W'),
    #     ('sepia', 'Sepia'),
    #     ('blur', 'Blur'), ],
    #     default='default',
    #     string="Thumbnail overlay effects")
    # no_extra_options = fields.Boolean(
    #     string='Slider effects',
    #     default=True,
    #     help="Slider with all options for next, previous, play, pause, fullscreen, hide/show thumbnail panel.")
    # change_thumbnail_size = fields.Boolean(string="Change thumbnail size", default=False)
    # thumb_height = fields.Char(string='Thumb height', default=50)
    # thumb_width = fields.Char(string='Thumb width', default=88)

    # @api.multi
    # def get_multiple_images(self, product_id=None):
    #     productsss = False
    #     if product_id:
    #         products = self.env['product.images'].search(
    #             [('product_variant_id', '=', product_id)])
    #         if products:
    #             return products
    #     return productsss

    # @api.multi
    # def get_product_variants(self,product_tmpl_id=None):
    #     productsss = False
    #     if product_tmpl_id:
    #         products = self.env['product.product'].search(
    #             [('product_tmpl_id', '=', product_tmpl_id)])
    #         if products:
    #             return products
    #     return productsss 
        

# class ResConfigSettings(models.TransientModel):

#     _inherit = 'res.config.settings'

#     thumbnail_panel_position = fields.Selection([
#         ('left', 'Left'),
#         ('right', 'Right'),
#         ('bottom', 'Bottom')],
#         string='Thumbnails panel position',
#         related='website_id.thumbnail_panel_position',
#         help="Select the position where you want to display the thumbnail panel in multi image.", readonly=False)
#     interval_play = fields.Char(
#         string='Play interval of slideshow',
#         related='website_id.interval_play',
#         help='With this field you can set the interval play time between two images.', readonly=False)
#     enable_disable_text = fields.Boolean(
#         string='Enable the text panel',
#         related='website_id.enable_disable_text',
#         help='Enable/Disable text which is visible on the image in multi image.', readonly=False)
#     color_opt_thumbnail = fields.Selection([
#         ('default', 'Default'),
#         ('b_n_w', 'B/W'),
#         ('sepia', 'Sepia'),
#         ('blur', 'Blur')],
#         related='website_id.color_opt_thumbnail',
#         string="Thumbnail overlay effects", readonly=False)
#     no_extra_options = fields.Boolean(
#         string='Slider effects',
#         # default=True,
#         related='website_id.no_extra_options',
#         help="Slider with all options for next, previous, play, pause, fullscreen, hide/show thumbnail panel.", readonly=False)
#     change_thumbnail_size = fields.Boolean(
#         string="Change thumbnail size",
#         related="website_id.change_thumbnail_size", readonly=False)
#     thumb_height = fields.Char(
#         string='Thumb height',
#         related="website_id.thumb_height", readonly=False)
#     thumb_width = fields.Char(
#         string='Thumb width',
#         related="website_id.thumb_width", readonly=False)

class MailMessage(models.Model):
    _inherit = 'res.partner'



    @api.multi
    def check_user_type(self, product_id=None):
        temp=0
        user_type=self.env['res.users'].sudo().search([('partner_id','=',self.id)])
        type_user=user_type.has_group('base.group_user') 
        if type_user == True:
            temp=1
        else:
            temp=0

        listtemp=[product_id,temp]
        
        return listtemp