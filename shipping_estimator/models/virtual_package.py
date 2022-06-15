from odoo import models, fields


class VirtualPackage(models.Model):
    _name = 'virtual.package'
    _description = 'Virtual Package'

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Package ID')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    shipment_id = fields.Many2one('stock.picking', string='Shipment ID')
    contents = fields.Char(string='Contents', help='general description of contents')
    dim1 = fields.Integer(string='Dimension 1')
    dim2 = fields.Integer(string='Dimension 2')
    dim3 = fields.Integer(string='Dimension 3')
    weight = fields.Integer(string='Weight', help='weight from adding package contents')
    dim_weight = fields.Integer(string='Dimension Weight', help='weight determined by package measurements')
    billing_weight = fields.Integer(string='Billing Weight')
    container_id = fields.Many2one('product.product', string='Container ID')
    container_name = fields.Char(related="container_id.name", string="Container Name")
    surcharge = fields.Float(string="Surcharge", help='sum of product and container surcharges')
    additional_handling_charges = fields.Float(string="Additional Handling Charges")
    extended_area_charge = fields.Float(string="Extended Area Charge")
    rate = fields.Float(string="Rate")
