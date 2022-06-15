# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class CheckStock(models.TransientModel):
    _name = "check.stock"
    _description = "Check Stock"
 
    # this function is not use any where
    # @api.multi
    # def update_lines(self):
    #     sale_line_ids = self.env['sale.order.line'].search([('id', 'in', self._context['selected_rec'])])
    

    # @api.depends('test')
    # def analyze_sale_order(self):
    #     if self._context.get('o2m_selection'):
    #         sale_order_line_ids = self.env['sale.order.line'].browse(self._context.get('o2m_selection'))
    #         order_lines = []
    #         for line in sale_line_obj:
    #             val = {
    #                 'product_id':line.product_id.id,
    #                 'current_stock':line.product_id.qty_available,
    #                 'incoming_stock':line.product_id.incoming_qty,
    #                 'requested_qty':line.product_uom_qty,
    #             }
    #             order_lines.append((0,0,val))
    #         self.data_line = order_lines



    # test = fields.Boolean(string='Test', default=True)

    @api.multi
    def update_lines(self):
        sale_line_ids = self.env['sale.order.line'].search([('id', 'in', self._context['selected_rec'])])

    data_line = fields.One2many('check.stock.line', string='Data Line', store=False)
    completed_date = fields.Date(string='Complete')


class CheckStockLine(models.TransientModel):
    _name = "check.stock.line"
    _description = "Check Stock Line"

    check_stock_id = fields.Many2one('check.stock', string='Wizard')
    product_id = fields.Many2one('product.product', string="Product")
    expected_date = fields.Date(string='Available')
    current_stock = fields.Float(string='Stock')
    incoming_stock = fields.Float(string='Purchases')
    requested_qty = fields.Float(string='Required')
    # supply_days = fields. Integer(string='Supply')