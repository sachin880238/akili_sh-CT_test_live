from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_line_stock_number = fields.Char(related="product_id.default_code", string='Order Line Stock Number')

    @api.onchange('product_id', 'product_template_id')
    def _onchange_product_id(self):
        if self.product_id:
            required_fields = {
                'Packing Category': self.product_id.packing_category,
                'Dimension 1': self.product_id.dim1,
                'Dimension 2': self.product_id.dim2,
                'Dimension 3': self.product_id.dim3,
                'Each additional 3': self.product_id.dim3_increment,
                'Weight': self.product_id.weight,
                'Cross Section': self.product_id.cross_section,
                'Volume': self.product_id.volume,
                'Surcharge per Item': self.product_id.product_surcharge,
                'Surcharge per Line': self.product_id.line_surcharge
            }

            empty_values = [field for field in required_fields if not required_fields[field]]
            if empty_values:
                count = 1
                text = ""
                for value in empty_values:
                    text += str(count) + ". " + value + "\n"
                    count += 1
                raise ValidationError(_('Please provide required details of product to sold this product.. \n\n %s') % text)
