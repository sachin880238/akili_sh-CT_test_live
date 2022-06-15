# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_loc_reservable = fields.Boolean("Reservable Location?")