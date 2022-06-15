# -*- coding: utf-8 -*-
from odoo import models, api


class CustomInit(models.Model):
    _name = 'custom.init'
    _description = 'Custom Init'

    @api.model
    def signup_enable(self):
        base_settings_obj = self.env['res.config.settings']
        base_settings_id = base_settings_obj.create({
            'auth_signup_uninvited': 'b2c',
             'template_user_id': True,
              'auth_signup_reset_password': True
        })
        base_settings_id.execute()
        return True

    @api.model
    def sales_settings(self):
        sale_settings_obj = self.env['res.config.settings']

        vals = {
            'group_use_lead': 1,
            'group_product_variant': 1,
            'group_uom': 1,
            'default_invoice_policy': 'delivery',
            'sale_pricelist_setting': 'formula',
            'group_sale_delivery_address': 1,
            'group_discount_per_so_line': 1,
            'add_prepayment_test': True,
            'over_credit_limit': True,
            'group_route_so_lines': 1,
            'group_mrp_properties': 1,
            'module_sale_order_dates': 1,
            'module_website_quote': 1,
            'module_delivery': 1,
            'alpha_color': '#000000',
            'bg_color': '#CCCCCC'
        }

        sale_settings_id = sale_settings_obj.create(vals)
        sale_settings_id.execute()
        return True

    @api.model
    def stock_settings(self):
        stock_settings_obj = self.env['res.config.settings']

        vals = {
            'group_stock_production_lot': 1,
            'group_stock_tracking_lot': 1,
            'module_stock_barcode': True,
            'group_stock_inventory_valuation': 1,
            'module_delivery_ups': True,
            'module_delivery_usps': True,
            'warehouse_and_location_usage_level': 2,
            'group_stock_adv_location': 1,
            'module_stock_dropshipping': 1,
            'module_stock_picking_wave': 1,
            'module_stock_calendar': 1,
            'group_uom': 1,
            'group_product_variant': 1,
            'module_quality': True,
        }

        stock_settings_id = stock_settings_obj.create(vals)
        stock_settings_id.execute()
        return True

    @api.model
    def website_settings(self):
        website_settings_obj = self.env['res.config.settings']

        website_content_id = self.env.ref(
            'custom_init.conservation_technology_content').id

        vals = {
            'website_content_id': website_content_id,
            'logout_timer': 12000
        }

        website_settings_id = website_settings_obj.create(vals)
        website_settings_id.execute()
        return True
