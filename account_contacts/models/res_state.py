# -*- coding: utf-8 -*-
# Copyright 2019 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.osv import expression
import logging
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class CountryState(models.Model):
    _inherit = 'res.country.state'

    sequence = fields.Integer(string='Sequence')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.code + ' ' + '-' + ' ' + record.name
            result.append((record.id, "{} - {}".format(record.code, record.name)))
        return result



class StateCountry(models.Model):
    _inherit = 'res.country'

    sequence = fields.Integer(string='Sequence')
    
