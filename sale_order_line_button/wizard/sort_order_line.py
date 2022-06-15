# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SortOrderLine(models.TransientModel):
    _name = "sort.order.line"
    _description = "Sort Order Line"

    sort_lines = fields.Selection([('sort_by_shipment', 'sort by shipment'),
       ('sort_in_sequence_created', 'sort in sequence created'),
       ('sort_in_reverse_of_sequence_created', 'sort in reverse of sequence created'), 
       ])

    @api.multi
    def sort_order_lines(self):
        if not self.sort_lines :
            raise UserError(_('Please Select sorting type'))
        sale_line_obj = self.env['sale.order.line']
        active_id = self.env.context.get('active_id')
        order_line = self.env['sale.order'].browse(int(active_id))
        create_date=[]
        if self.sort_lines=='sort_in_sequence_created':
            for rec in order_line.order_line:
                create_date.append(rec.create_date)
            i=0
            create_date.sort()
            for rec in order_line.order_line:
                for length in range(0,len(create_date)):
                    if create_date[length]==rec.create_date:
                        rec.sequence=length
            
        if self.sort_lines=='sort_in_reverse_of_sequence_created':
            for rec in order_line.order_line:
                create_date.append(rec.create_date)
            i=0
            create_date.sort(reverse = True)
            for rec in order_line.order_line:
                for length in range(0,len(create_date)):
                    if create_date[length]==rec.create_date:
                        rec.sequence=length
