from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import logging
from odoo.http import request


class PolCheckStock(models.TransientModel):
    _name = "pol.check.stock"
    _description = "Purchase order line Check Stock"


    # @api.multi
    # def update_lines(self):
    #     sale_line_ids = self.env['sale.order.line'].search([('id', 'in', self._context['selected_rec'])])

    data_line = fields.One2many('pol.check.stock.line', string='Data Line', store=False) 

    completed_date = fields.Date(string='Complete')


class PoCheckStockLine(models.TransientModel):
    _name = "pol.check.stock.line"
    _description = "Pol Check Stock Line"

    check_stock_id = fields.Many2one('po.check.stock', string='Wizard')
    product_id = fields.Many2one('product.product', string="Product")
    expected_date = fields.Date(string='Available')
    current_stock = fields.Float(string='Stock')
    incoming_stock = fields.Float(string='Purchases')
    requested_qty = fields.Float(string='Required')