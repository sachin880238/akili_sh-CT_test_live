# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class NmfcClass(models.Model):
    _name = "nmfc.class"
    _description = "National Motor Freight Classification"
    _rec_name = "code"

    code = fields.Char("Code")
    description = fields.Char("Description")
    nmfc_class = fields.Char("Class")
