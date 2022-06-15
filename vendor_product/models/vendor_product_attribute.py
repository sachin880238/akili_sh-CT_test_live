from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class VendorProductAttribute(models.Model):
    _name = "vendor.product.attribute"
    _description = "Vendor Product Attribute"
    # if you change this _order, keep it in sync with the method
    # `_sort_key_attribute_value` in `vendor.product.template`
    _order = 'sequence, id'

    name = fields.Char('Attribute', required=True, translate=True)
    value_ids = fields.One2many('vendor.product.attr.value', 'attribute_id', 'Values', copy=True)
    sequence = fields.Integer('Sequence', help="Determine the display order", index=True)
    attribute_line_ids = fields.One2many('vendor.product.template.attr.line', 'attribute_id', 'Lines')
    create_variant = fields.Selection([
        ('no_variant', 'Never'),
        ('always', 'Always'),
        ('dynamic', 'Only when the product is added to a sales order')],
        default='always',
        string="Create Variants",
        help="Check this if you want to create multiple variants for this attribute.", required=True)

    @api.multi
    def _without_no_variant_attributes(self):
        return self.filtered(lambda pa: pa.create_variant != 'no_variant')

    @api.multi
    def write(self, vals):
        """Override to make sure attribute type can't be changed if it's used on
        a product template.

        This is important to prevent because changing the type would make
        existing combinations invalid without recomputing them, and recomputing
        them might take too long and we don't want to change products without
        the user knowing about it."""
        if 'create_variant' in vals:
            products = self._get_related_product_templates()
            if products:
                message = ', '.join(products.mapped('name'))
                raise UserError(_('You are trying to change the type of an attribute value still referenced on at least one product template: %s') % message)
        invalidate_cache = 'sequence' in vals and any(record.sequence != vals['sequence'] for record in self)
        res = super(VendorProductAttribute, self).write(vals)
        if invalidate_cache:
            # prefetched o2m have to be resequenced
            # (eg. vendor.product.template: attribute_line_ids)
            self.invalidate_cache()
        return res

    @api.multi
    def _get_related_product_templates(self):
        return self.env['vendor.product.template'].with_context(active_test=False).search([
            ('attribute_line_ids.attribute_id', 'in', self.ids),
        ])


class VendorProductAttributeValue(models.Model):
    _name = "vendor.product.attr.value"
    # if you change this _order, keep it in sync with the method
    # `_sort_key_variant` in `vendor.product.template'
    _order = 'attribute_id, sequence, id'
    _description = 'Attribute Value'

    name = fields.Char(string='Value', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', help="Determine the display order", index=True)
    attribute_id = fields.Many2one('vendor.product.attribute', string='Attribute', ondelete='cascade', required=True, index=True)

    _sql_constraints = [
        ('value_company_uniq', 'unique (name, attribute_id)', 'This attribute value already exists !')
    ]

    @api.multi
    def name_get(self):
        if not self._context.get('show_attribute', True):  # TDE FIXME: not used
            return super(VendorProductAttributeValue, self).name_get()
        return [(value.id, "%s: %s" % (value.attribute_id.name, value.name)) for value in self]

    @api.multi
    def _variant_name(self, variable_attributes):
        return ", ".join([v.name for v in self if v.attribute_id in variable_attributes])

    @api.multi
    def write(self, values):
        invalidate_cache = 'sequence' in values and any(record.sequence != values['sequence'] for record in self)
        res = super(VendorProductAttributeValue, self).write(values)
        if invalidate_cache:
            # prefetched o2m have to be resequenced
            # (eg. vendor.product.template.attr.line: value_ids)
            self.invalidate_cache()
        return res

    @api.multi
    def unlink(self):
        linked_products = self._get_related_product_templates()
        if linked_products:
            raise UserError(_('The operation cannot be completed:\nYou are trying to delete an attribute value with a reference on a product variant.'))
        return super(VendorProductAttributeValue, self).unlink()

    @api.multi
    def _without_no_variant_attributes(self):
        return self.filtered(lambda pav: pav.attribute_id.create_variant != 'no_variant')

    @api.multi
    def _get_related_product_templates(self):
        return self.env['vendor.product.template'].with_context(active_test=False).search([
            ('attribute_line_ids.value_ids', 'in', self.ids),
        ])


class VendorProductTemplateAttributeLine(models.Model):
    """Attributes available on vendor.product.template with their selected values in a m2m.
    Used as a configuration model to generate the appropriate vendor.product.template.attribute.value"""

    _name = "vendor.product.template.attr.line"
    _rec_name = 'attribute_id'
    _description = 'Vendor Product Template Attribute Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence')
    product_tmpl_id = fields.Many2one('vendor.product.template', string='Product Template', ondelete='cascade', required=True, index=True)
    attribute_id = fields.Many2one('vendor.product.attribute', string='Attribute', ondelete='restrict', required=True, index=True)
    value_ids = fields.Many2many('vendor.product.attr.value', string='Values')
    product_template_value_ids = fields.Many2many(
        'vendor.product.template.attribute.value',
        string='Product Attribute Values',
        compute="_set_product_template_value_ids",
        store=False)
    before = fields.Char(string='Before')
    after = fields.Char(string='After')

    @api.constrains('value_ids', 'attribute_id')
    def _check_valid_attribute(self):
        if any(not line.value_ids or line.value_ids > line.attribute_id.value_ids for line in self):
            raise ValidationError(_('You cannot use this attribute with the following value.'))
        return True

    @api.model
    def create(self, values):
        if not values['value_ids']:
            raise UserError(_('Attriute value is required to create Product Template.'))
        attr_line = self.search([('product_tmpl_id', '=', values['product_tmpl_id'])])
        values['sequence'] = len(attr_line) + 1
        res = super(VendorProductTemplateAttributeLine, self).create(values)
        res._update_product_template_attribute_values()
        return res

    def write(self, values):
        res = super(VendorProductTemplateAttributeLine, self).write(values)
        self._update_product_template_attribute_values()

        if 'attribute_id' in values:
            # delete remaining vendor.product.template.attribute.value that are not used on any line
            product_template_attribute_values_to_remove = self.env['vendor.product.template.attribute.value']
            for product_template in self.mapped('product_tmpl_id'):
                product_template_attribute_values_to_remove += product_template_attribute_values_to_remove.search([
                    ('product_tmpl_id', '=', product_template.id),
                    ('product_attribute_value_id', 'not in', product_template.attribute_line_ids.mapped('value_ids').ids),
                ])
            product_template_attribute_values_to_remove.unlink()

        return res

    @api.depends('value_ids')
    def _set_product_template_value_ids(self):
        for product_template_attribute_line in self:
            product_template_attribute_line.product_template_value_ids = self.env['vendor.product.template.attribute.value'].search([
                ('product_tmpl_id', 'in', product_template_attribute_line.product_tmpl_id.ids),
                ('product_attribute_value_id', 'in', product_template_attribute_line.value_ids.ids)]
            )

    @api.multi
    def unlink(self):
        for product_template_attribute_line in self:
            self.env['vendor.product.template.attribute.value'].search([
                ('product_tmpl_id', 'in', product_template_attribute_line.product_tmpl_id.ids),
                ('product_attribute_value_id.attribute_id', 'in', product_template_attribute_line.value_ids.mapped('attribute_id').ids)]).unlink()

        return super(VendorProductTemplateAttributeLine, self).unlink()

    def _update_product_template_attribute_values(self):
        """
        Create or unlink vendor.product.template.attribute.value based on the attribute lines.
        If the vendor.product.attr.value is removed, remove the corresponding vendor.product.template.attribute.value
        If no vendor.product.template.attribute.value exists for the newly added vendor.product.attr.value, create it.
        """
        for attribute_line in self:
            # All existing vendor.product.template.attribute.value for this template
            product_template_attribute_values_to_remove = self.env['vendor.product.template.attribute.value'].search([
                ('product_tmpl_id', '=', attribute_line.product_tmpl_id.id),
                ('product_attribute_value_id.attribute_id', 'in', attribute_line.value_ids.mapped('attribute_id').ids)])
            # All existing vendor.product.attr.value shared by all products
            # eg (Yellow, Red, Blue, Small, Large)
            existing_product_attribute_values = product_template_attribute_values_to_remove.mapped('product_attribute_value_id')

            # Loop on vendor.product.attr.values for the line (eg: Yellow, Red, Blue)
            for product_attribute_value in attribute_line.value_ids:
                if product_attribute_value in existing_product_attribute_values:
                    # property is already existing: don't touch, remove it from list to avoid unlinking it
                    product_template_attribute_values_to_remove = product_template_attribute_values_to_remove.filtered(
                        lambda value: product_attribute_value not in value.mapped('product_attribute_value_id')
                    )
                else:
                    # property does not exist: create it
                    self.env['vendor.product.template.attribute.value'].create({
                        'product_attribute_value_id': product_attribute_value.id,
                        'product_tmpl_id': attribute_line.product_tmpl_id.id})

            # at this point, existing properties can be removed to reflect the modifications on value_ids
            if product_template_attribute_values_to_remove:
                product_template_attribute_values_to_remove.unlink()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        # TDE FIXME: currently overriding the domain; however as it includes a
        # search on a m2o and one on a m2m, probably this will quickly become
        # difficult to compute - check if performance optimization is required
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            domain = ['|', ('attribute_id', operator, name), ('value_ids', operator, name)]
            attribute_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
            return self.browse(attribute_ids).name_get()
        return super(VendorProductTemplateAttributeLine, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.multi
    def _without_no_variant_attributes(self):
        return self.filtered(lambda ptal: ptal.attribute_id.create_variant != 'no_variant')


class VendorProductTemplateAttributeValue(models.Model):
    """Materialized relationship between attribute values
    and product template generated by the vendor.product.template.attr.line"""

    _name = "vendor.product.template.attribute.value"
    _order = 'product_attribute_value_id, id'
    _description = 'Vendor Product Attribute Value'

    name = fields.Char('Value', related="product_attribute_value_id.name")
    product_attribute_value_id = fields.Many2one(
        'vendor.product.attr.value', string='Attribute Value',
        required=True, ondelete='cascade', index=True)
    product_tmpl_id = fields.Many2one(
        'vendor.product.template', string='Product Template',
        required=True, ondelete='cascade', index=True)
    attribute_id = fields.Many2one(
        'vendor.product.attribute', string='Attribute',
        related="product_attribute_value_id.attribute_id")
    sequence = fields.Integer('Sequence', related="product_attribute_value_id.sequence")
    exclude_for = fields.One2many(
        'vendor.product.template.attribute.exclusion',
        'product_template_attribute_value_id',
        string="Exclude for",
        relation="product_template_attribute_exclusion",
        help="""Make this attribute value not compatible with
        other values of the product or some attribute values of optional and accessory products.""")

    @api.multi
    def name_get(self):
        if not self._context.get('show_attribute', True):  # TDE FIXME: not used
            return super(VendorProductTemplateAttributeValue, self).name_get()
        return [(value.id, "%s: %s" % (value.attribute_id.name, value.name)) for value in self]

    @api.multi
    def _without_no_variant_attributes(self):
        return self.filtered(lambda ptav: ptav.attribute_id.create_variant != 'no_variant')


class VendorProductTemplateAttributeExclusion(models.Model):
    _name = "vendor.product.template.attribute.exclusion"
    _description = 'Vendor Product Template Attribute Exclusion'

    product_template_attribute_value_id = fields.Many2one(
        'vendor.product.template.attribute.value', string="Attribute Value", ondelete='cascade', index=True)
    product_tmpl_id = fields.Many2one(
        'vendor.product.template', string='Product Template', ondelete='cascade', required=True, index=True)
    value_ids = fields.Many2many(
        'vendor.product.template.attribute.value', relation="product_attr_exclusion_value_ids_rel",
        string='Values', domain="[('product_tmpl_id', '=', product_tmpl_id)]")
