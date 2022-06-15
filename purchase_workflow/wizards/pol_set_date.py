# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from datetime import datetime, date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class polSetDate(models.TransientModel):
    _name = "pol.set.date"
    _description = "Purchase Order Line Set date"

    set_date = fields.Selection([
        ('date_default_product', 'set Date based on product defaults'),
        ('date_lead_time', 'set Date based on current lead time'),
        ('date_eliminate_backorder', 'set Date to eliminate backorders'),
        ('date_to', 'set Date to')
        ])
    delivery_date = fields.Date(string='Delivery Date')

    @api.multi
    def set_date_selected_orderlines(self):
            po_line_ids = self.env['purchase.order.line'].browse(self._context.get('o2m_selection').get('order_line').get('ids'))
        
            if self.set_date == 'date_to':
                for line in po_line_ids:
                    line.date_planned = str(self.delivery_date)

            elif self.set_date == 'date_default_product':
                for line in po_line_ids:
                    delivery_date = date.today() + timedelta(days=line.product_id.sale_delay)
                    delivery_date_str = datetime.strftime(delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    line.date_planned = delivery_date_str

            elif self.set_date == 'date_lead_time':
                for line in po_line_ids:
                    delivery_date = date.today() + timedelta(days=line.product_id.produce_delay)
                    delivery_date_str = datetime.strftime(delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    line.date_planned = delivery_date_str