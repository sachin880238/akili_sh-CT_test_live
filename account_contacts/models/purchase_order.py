from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    priority = fields.Selection([(' ', 'Very Low'), ('x', 'Low'), ('xx', 'Normal'), ('xxx', 'High')], string='Priority',index="True")
    sub_state2 = fields.Selection([('create', 'DRAFT'),('review', 'REVIEW'), ('revise', 'REVISE'), ('wait', 'WAIT'),('send','SEND'),('confirm','CONFIRM') ], default='create',
        track_visibility='onchange', readonly=True, copy=False,string="Stages")
    products = fields.Char(related="partner_id.products_purchased", string="Products")
    reviewer_id = fields.Many2one('res.users', string='Reviewer', index=True)