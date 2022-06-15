from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # @api.model
    # def create(self, vals):
    #     print"Create Template Call form BOM file",vals
    #     res = super(ProductTemplate, self).create(vals)
    #     return res

    @api.multi
    def write(self,vals):
        for id in self:
            if 'product_type' in vals:
                if vals['product_type'] == 'set':
                    if id.bom_count == 0:
                        raise UserError(_("Default Set Is required !!!!!!")) 
        res = super(ProductTemplate, self).write(vals)
        return res

    templ_bom_line_id = fields.Many2one("mrp.bundle.line","Templ Bom")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # @api.model
    # def create(self, vals):
    #     res = super(ProductProduct, self).create(vals)
    #     return res


    var_bom_line_id = fields.Many2one("mrp.bundle.line","Var Bom")

    @api.multi
    def write(self,vals):
        for id in self:
            if 'product_type' in vals:
                if vals['product_type'] == 'set':
                    if id.bom_count == 0:
                        raise UserError(_("Default Set Is required !!!!!!"))   
        res = super(ProductProduct, self).write(vals)
        return res


    @api.multi
    def action_view_bom(self):
        action = super(ProductProduct,self).action_view_bom()
        action['context'].update({'default_from_product':True})
        action['context'].update({'product_id': self.ids[0]})
        return action

    def _compute_bom_count(self):
        read_group_res = self.env['mrp.bom'].read_group([('product_id', 'in', self.ids)], ['product_id'], ['product_id'])
        mapped_data = dict([(data['product_id'][0], data['product_id_count']) for data in read_group_res])
        for product in self:
            if product.product_tmpl_id.product_variant_count == 1:
                bom_count = mapped_data.get(product.id, product.product_tmpl_id.bom_count)
            else:
                mrp_bom_count = self.env['mrp.bom'].search_count(
                    ['|','&',('product_tmpl_id', '=', product.product_tmpl_id.id),
                        ('product_id','=',False),
                        ('product_id', 'in', self.ids)
                    ])
                bom_count = mrp_bom_count
            product.bom_count = bom_count
