# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from datetime import datetime, date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SetDateOrderLine(models.TransientModel):
    _name = "set.date.orderline"
    _description = "Set date Orderline"

    set_date = fields.Selection([
        ('date_default_product', 'set Date based on product defaults'),
        ('date_lead_time', 'set Date based on current lead time'),
        ('date_eliminate_backorder', 'set Date to eliminate backorders'),
        ('date_to', 'set Date to')
        ])
    delivery_date = fields.Date(string='Delivery Date')

    @api.multi
    def set_date_selected_orderlines(self):
        if self._context.get('sale_order_line'):
            sale_order_line_ids = self.env['sale.order.line'].browse(self._context.get('sale_order_line'))

            if self.set_date == 'date_to':
                for line in sale_order_line_ids:
                    line.delivery_date = str(self.delivery_date)
            elif self.set_date == 'date_default_product':
                for line in sale_order_line_ids:
                    delivery_date = date.today() + timedelta(days=line.product_id.sale_delay)
                    delivery_date_str = datetime.strftime(delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    line.delivery_date = delivery_date_str
            elif self.set_date == 'date_lead_time':
                for line in sale_order_line_ids:
                    delivery_date = date.today() + timedelta(days=line.product_id.produce_delay)
                    delivery_date_str = datetime.strftime(delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    line.delivery_date = delivery_date_str