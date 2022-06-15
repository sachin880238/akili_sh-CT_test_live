# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ShippingContainer(models.Model):
    _name = 'shipping.container'
    _description = 'Shipping Container'
    _rec_name = 'container_name'

    _order = 'sequence'
    sequence = fields.Integer(string='sequence')


    container_name = fields.Char(
        string='Container Name', help="Identifies container")
    container_type = fields.Selection(
        [
            ('ctube', 'Circular Tube'),
            ('ttube', 'Triangular Tube'),
            ('rtube', 'Rectangular Tube'),
            ('pboard', 'Protected Board'),
            ('box', 'Box'),
            ('crate', 'Crate')
        ], string='Container Type')

    container_dim1 = fields.Float(
        string='Container Dim1', help="Interior inches")
    container_dim2 = fields.Float(
        string='Container Dim2', help="Interior inches")
    container_dim3 = fields.Float(
        string='Container Dim3', help="Interior inches")
    container_billing_dim1 = fields.Float(
        string='Container Billing Dim1', help="Round up exterior inches")
    container_billing_dim2 = fields.Float(
        string='Container Billing Dim2', help="Round up exterior inches")
    container_billing_dim3 = fields.Float(
        string='Container Billing Dim3', help="Round up exterior inches")
    container_section = fields.Float(
        string='Container Section', help="Interior square inches of plane perpendicular to longest dimension")
    container_volume = fields.Float(
        string='Container Volume', help="Interior cubic inches")
    container_weight = fields.Float(
        string='Container Weight', help="Empty package weight")
    container_surcharge = fields.Float(
        string='Container Surcharge', help="Charge assessed for each container")