from odoo import fields, models, _

class StockDocuments(models.Model):
    _name = "stock.documents"
    _description = 'Stock Documents'  

    order = "sequence"
    sequence = fields.Integer(string='sequence', help="Gives the sequence order when displaying a list of product categories.")

    doc_type = fields.Char("Type")
    origin = fields.Char("Document")
    picking_id = fields.Many2one('stock.picking',"Picking")