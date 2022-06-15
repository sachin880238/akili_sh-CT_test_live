# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PolSortLine(models.TransientModel):
    _name = "pol.sort.line"
    _description = "Purchase order line Sort Line"

    sort_lines = fields.Selection([('sort_by_shipment', 'sort by shipment'),
       ('sort_in_sequence_created', 'sort in sequence created'),
       ('sort_in_reverse_of_sequence_created', 'sort in reverse of sequence created'), 
       ])

    @api.multi
    def sort_order_lines(self):
        if not self.sort_lines :
            raise UserError(_('Please Select sorting type'))
        po_line_obj = self.env['purchase.order.line']
        active_id = self.env.context.get('active_id')
        order_line = self.env['purchase.order'].browse(int(active_id))
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

        # so_line = sale_line_obj.with_context({'trigger_onchange': True,
        #     'onchange_fields_to_trigger': ['product_id', 'product_uom_qty']
        # }).create(values)
        # if self.sort_lines == 'sort_by_shipment':
        #   self.sort_by_shipment()




