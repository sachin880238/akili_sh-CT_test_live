

from openerp import models, fields, api, _ 
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    product_documents_ids = fields.One2many('ir.attachment','product_tmp_id', string='Product Document',)
    
    

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    product_documents_ids = fields.One2many('ir.attachment','product_id', string='Currency Symbol')

    @api.multi
    def have_published_document(self):
        return any(doc.public for doc in self.product_documents_ids)


class Attachment(models.Model):

    _inherit = "ir.attachment" 
    description = fields.Text(string='Description')
    file_type = fields.Selection([('file','File')],string='Type',default='file')  
 
    product_doc = fields.Boolean(string='Product Document')  
    create_date = fields.Date(string="Date")  
    public = fields.Boolean(string="Publish") 
    product_tmp_id = fields.Many2one('product.template', string="Product")
    product_id = fields.Many2one('product.product', string="Product")
    sequence = fields.Integer(string='Sequence', default=10)
    name= fields.Char(string='Document')