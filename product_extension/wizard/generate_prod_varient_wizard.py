import itertools
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from openerp.tools import frozendict

class GenerateProdVariant(models.TransientModel):
    _name = 'generate.prod.variant'
    _description = 'Generate Product Variants'

    load_attribute = fields.Boolean("Load Attributes", default=True)
    prod_attribute_line_ids = fields.One2many('generate.prod.variant.line','product_attribute_line_id', string="Generate Variants")
    
    @api.onchange('load_attribute')
    def onchange_load_attribute(self):
        if self.load_attribute==True:
            active_product_id=self.env['product.template'].search([('id', '=', self._context['active_id'])])
            datas=[]
            for rec in active_product_id.attribute_line_ids:
                product_attribute_id=rec.attribute_id.id
                if self._context.get('secondary'):
                    values={
                        'product_attribute_id':rec.attribute_id.id,
                        'template_variants_values_ids':[(6, 0, rec.value_ids.ids)]
                    }
                else:
                    values={
                    'product_attribute_id':rec.attribute_id.id,
                    'product_attribute_values_ids':[(6, 0, rec.value_ids.ids)],
                    'template_variants_values_ids':[(6, 0, rec.value_ids.ids)]
                    }
                datas.append((0, 0, values))
                self.update({'prod_attribute_line_ids':datas})
                datas = []
    
    @api.multi
    def generate_prod_variants(self):
        desire_values = []
        for line in self.prod_attribute_line_ids:
            for value in line.product_attribute_values_ids:
                desire_values.append(value.name)
        prod_temp_id = self.env['product.template'].search([('id','=',self._context['active_id'])])
        prod_temp_id.env.context = frozendict(prod_temp_id.env.context, generate_variant=True)
        prod_temp_id.create_variant_ids(desire_values)
        prod_temp_id.update_products_variants()
        if not self._context.get('secondary',False):
            prod_temp_id.update_product_images()
            for rec in prod_temp_id:
                rec.write({'status':'private'})
        return True

class GenerateProdVariantLine(models.TransientModel):
    _name = 'generate.prod.variant.line'
    _description = 'Generate Product variant lines' 
    

    product_attribute_line_id = fields.Many2one('generate.prod.variant')

    product_attribute_id = fields.Many2one('product.attribute', string="Attribute")
    product_attribute_values_ids = fields.Many2many('product.attribute.value', string="Value")
    template_variants_values_ids = fields.Many2many('product.attribute.value', string="Value",store=False)

    @api.constrains('product_attribute_values_ids', 'product_attribute_id')
    def _check_valid_attribute(self):
        if any(not line.product_attribute_values_ids for line in self):
            raise ValidationError(_('At least one Value must be selected for each Attribute.'))
        return True