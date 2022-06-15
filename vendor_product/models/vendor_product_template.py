import itertools

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from odoo.tools import pycompat


class VendorProductTemplate(models.Model):
    _name = "vendor.product.template"
    _description = "Vendor Product Template"

    days_to_ship = fields.Integer(string='Days To Ship')
    name = fields.Char('Vendor Product', required=True)
    product_description = fields.Char()
    sequence = fields.Integer('Sequence')
    vendor_description = fields.Text('Vendor Description')
    uom_ids = fields.Many2many('uom.uom', string='Units')
    state = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string="Stage", default='draft')
    active = fields.Boolean(
        'Active', help="If unchecked, it will allow you to hide the product without removing it.")
    is_product_variant = fields.Boolean(
        string='Is a product variant', compute='_compute_is_product_variant')
    attribute_line_ids = fields.One2many(
        'vendor.product.template.attr.line', 'product_tmpl_id', 'Product Attributes')

    valid_product_template_attribute_line_ids = fields.Many2many('vendor.product.template.attr.line',
                                                                 compute="_compute_valid_attributes", string='Valid Product Attribute Lines', help="Technical compute")
    valid_product_attribute_value_ids = fields.Many2many('vendor.product.attr.value',
                                                         compute="_compute_valid_attributes", string='Valid Product Attribute Values', help="Technical compute")
    valid_product_attribute_ids = fields.Many2many('vendor.product.attribute',
                                                   compute="_compute_valid_attributes", string='Valid Product Attributes', help="Technical compute")

    valid_product_template_attribute_line_wnva_ids = fields.Many2many('vendor.product.template.attr.line',
                                                                      compute="_compute_valid_attributes", string='Valid Product Attribute Lines Without No Variant Attributes', help="Technical compute")
    valid_product_attribute_value_wnva_ids = fields.Many2many('vendor.product.attr.value',
                                                              compute="_compute_valid_attributes", string='Valid Product Attribute Values Without No Variant Attributes', help="Technical compute")
    valid_product_attribute_wnva_ids = fields.Many2many('vendor.product.attribute',
                                                        compute="_compute_valid_attributes", string='Valid Product Attributes Without No Variant Attributes', help="Technical compute")
    # valid_archived_variant_ids deprecated
    valid_archived_variant_ids = fields.Many2many('vendor.product.product',
                                                  compute="_compute_valid_archived_variant_ids", string='Valid Archived Variants', help="Technical compute")
    # valid_existing_variant_ids deprecated
    valid_existing_variant_ids = fields.Many2many('vendor.product.product',
                                                  compute="_compute_valid_existing_variant_ids", string='Valid Existing Variants', help="Technical compute")

    product_variant_ids = fields.One2many(
        'vendor.product.product', 'product_tmpl_id', 'Products', required=True)
    # performance: product_variant_id provides prefetching on the first product variant only
    product_variant_id = fields.Many2one(
        'vendor.product.product', 'Product', compute='_compute_product_variant_id')

    product_variant_count = fields.Integer(
        '# Product Variants', compute='_compute_product_variant_count')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of the product. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved, "
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of the product. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    task_count = fields.Integer(string='Tasks')
    project_count = fields.Integer(string='Projects')
    document_count = fields.Integer(string='Documents')
    vendor_id = fields.Many2one('res.partner', string="Vendor", domain=[('supplier', '=', True),('parent_id', '=', False)])
    delivery_warning = fields.Char('Delivery Warning')
    invoice_warning = fields.Char('Invoice Warning')
    purchasing_comments = fields.Text('Purchasing Comments')
    dim1 = fields.Float(string='Dimension 1')
    dim2 = fields.Float(string='Dimension 2')
    dim3 = fields.Float(string='Dimension 3')
    each_additional3 = fields.Float(string='Each Additional 3')
    cross_section = fields.Float(string='Cross Section')
    volume = fields.Float(string='Volume')
    first_unit = fields.Float(string="First Unit")
    each_additional = fields.Float(string="Each Additional")
    nmfc_code = fields.Many2one('nmfc.class', string="NMFC Code")
    nmfc_desc = fields.Char(related='nmfc_code.description', string=' NMFC Description')
    nmfc_class = fields.Char(related='nmfc_code.nmfc_class', string='NMFC Class')
    truckload_qty = fields.Float(string='Truckload Quantity')
    hts_code = fields.Many2one('hts.description', string='HTS Code')
    hts_desc = fields.Char(related='hts_code.description', string='HTS Description')
    container_qty = fields.Char(string='Container Quantity')
    freight_bill_warn = fields.Char(string='Freight Bill Warning')
    shipping_comments = fields.Text(string='Shipping Comments')
    demo_attribute_ids = fields.Char(string='Attribute Values')
    vendor_stock_id = fields.Char(string='Vendor Stock ID')
    vendor_price_ids = fields.One2many('vendor.price', 'product_tmpl_id', 'Vendor Price', domain=[('product_id', '=', False)])

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_vendor_product_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_vendor_product_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"
                
    def reset_to_draft(self):
        self.active = False
        self.state = 'draft'
        product_variants = self.env['vendor.product.product'].search([('product_tmpl_id', '=', self.id)])
        if product_variants:
            product_variants.write({'state': 'draft'})

    def active_template(self):
        self.active = True
        self.state = 'active'
        product_variants = self.env['vendor.product.product'].search([('product_tmpl_id', '=', self.id)])
        if product_variants:
            product_variants.write({'state': 'active'})

    def deactivate_template(self):
        self.active = False
        self.state = 'inactive'
        product_variants = self.env['vendor.product.product'].search([('product_tmpl_id', '=', self.id)])
        if product_variants:
            product_variants.write({'state': 'inactive'})

    # primary generate button
    @api.multi
    def generate_variants(self):
        wizard_form = self.env.ref('vendor_product.generate_prod_variant_wizard_view', False)
        return {
            'name': _('Generate Variants'),
            'type': 'ir.actions.act_window',
            'res_model': 'generate.vendor.prod.variant',
            'view_id': wizard_form.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }

    # secondary generate button
    @api.multi
    def generate(self):
        wizard_form = self.env.ref('vendor_product.generate_prod_variant_wizard_view', False)
        return {
            'name': _('Generate Variants'),
            'type': 'ir.actions.act_window',
            'res_model': 'generate.vendor.prod.variant',
            'view_id': wizard_form.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'secondary': True},
            'target': 'new'
        }

    def product_documents(self):
        return

    @api.depends('product_variant_ids')
    def _compute_product_variant_id(self):
        for p in self:
            p.product_variant_id = p.product_variant_ids[:1].id

    def _compute_is_product_variant(self):
        for template in self:
            template.is_product_variant = False


    @api.one
    @api.depends('product_variant_ids.product_tmpl_id')
    def _compute_product_variant_count(self):
        # do not pollute variants to be prefetched when counting variants
        self.product_variant_count = len(
            self.with_prefetch().product_variant_ids)

    @api.constrains('attribute_line_ids')
    def _check_attribute_line(self):
        if any(len(template.attribute_line_ids) != len(template.attribute_line_ids.mapped('attribute_id')) for template in self):
            raise ValidationError(
                _('You cannot define two attribute lines for the same attribute.'))
        return True

    @api.model_create_multi
    def create(self, vals_list):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        # TDE FIXME: context brol
        for vals in vals_list:
            tools.image_resize_images(vals)
        templates = super(VendorProductTemplate, self).create(vals_list)
        if "create_product_product" not in self._context:
            templates.with_context(create_from_tmpl=True).create_variant_ids()

        # This is needed to set given values to first variant after creation
        for template, vals in pycompat.izip(templates, vals_list):
            related_vals = {}
            if related_vals:
                template.write(related_vals)


        return templates

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(VendorProductTemplate, self).write(vals)   
        if 'attribute_line_ids' in vals or vals.get('active'):
            self.create_variant_ids()
        if 'active' in vals and not vals.get('active'):
            self.with_context(active_test=False).mapped(
                'product_variant_ids').write({'active': vals.get('active')})
        return res

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # TDE FIXME: should probably be copy_data
        self.ensure_one()
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)") % self.name
        return super(VendorProductTemplate, self).copy(default=default)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        # Only use the vendor.product.product heuristics if there is a search term and the domain
        # does not specify a match on `product.template` IDs.
        if not name or any(term[0] == 'id' for term in (args or [])):
            return super(VendorProductTemplate, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

        Product = self.env['vendor.product.product']
        templates = self.browse([])
        domain_no_variant = [('product_variant_ids', '=', False)]
        while True:
            domain = templates and [
                ('product_tmpl_id', 'not in', templates.ids)] or []
            args = args if args is not None else []
            products_ns = Product._name_search(
                name, args + domain, operator=operator, name_get_uid=name_get_uid)
            products = Product.browse([x[0] for x in products_ns])
            templates |= products.mapped('product_tmpl_id')
            current_round_templates = self.browse([])
            if not products:
                domain_template = args + domain_no_variant + \
                    (templates and [('id', 'not in', templates.ids)] or [])
                template_ns = super(VendorProductTemplate, self)._name_search(
                    name=name, args=domain_template, operator=operator, limit=limit, name_get_uid=name_get_uid)
                current_round_templates |= self.browse(
                    [ns[0] for ns in template_ns])
                templates |= current_round_templates
            if (not products and not current_round_templates) or (limit and (len(templates) > limit)):
                break

        # re-apply product.template order + name_get
        return super(VendorProductTemplate, self)._name_search(
            '', args=[('id', 'in', list(set(templates.ids)))],
            operator='ilike', limit=limit, name_get_uid=name_get_uid)

    @api.multi
    def create_variant_ids(self, desire_values=[]):
        product = self.env["vendor.product.product"]
        if "generate_variant" not in self._context:
            return False

        for tmpl_id in self.with_context(active_test=False):
            # Handle the variants for each template separately. This will be
            # less efficient when called on a lot of products with few variants
            # but it is better when there's a lot of variants on one template.
            variants_to_create = []
            variants_to_activate = self.env['vendor.product.product']
            variants_to_unlink = self.env['vendor.product.product']
            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            variant_alone = tmpl_id._get_valid_product_template_attribute_lines().filtered(
                lambda line: line.attribute_id.create_variant == 'always' and len(line.value_ids) == 1).mapped('value_ids')
            for value_id in variant_alone:
                updated_products = tmpl_id.product_variant_ids.filtered(
                    lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
                updated_products.write(
                    {'attribute_value_ids': [(4, value_id.id)]})

            # Determine which product variants need to be created based on the attribute
            # configuration. If any attribute is set to generate variants dynamically, skip the
            # process.
            # Technical note: if there is no attribute, a variant is still created because
            # 'not any([])' and 'set([]) not in set([])' are True.
            if not tmpl_id.has_dynamic_attributes():
                # Iterator containing all possible `vendor.product.attr.value` combination
                # The iterator is used to avoid MemoryError in case of a huge number of combination.
                all_variants = itertools.product(*(
                    line.value_ids.ids for line in tmpl_id.valid_product_template_attribute_line_wnva_ids
                ))
                # Set containing existing `vendor.product.attr.value` combination
                existing_variants = {
                    frozenset(variant.attribute_value_ids.ids)
                    for variant in tmpl_id.product_variant_ids
                }
                # For each possible variant, create if it doesn't exist yet.
                for value_ids in all_variants:
                    price_ids = [price for price in tmpl_id.vendor_price_ids]
                    exist_in_wizard = []
                    value_ids = frozenset(value_ids)
                    if value_ids not in existing_variants:
                        for attr in value_ids:
                            attr_id = self.env['vendor.product.attr.value'].search([('id', '=', attr)])
                            if attr_id.name in desire_values:
                                exist_in_wizard.append(True)
                            else:
                                exist_in_wizard.append(False)
                        if all(exist_in_wizard):
                            variants_to_create.append({
                                'product_tmpl_id': tmpl_id.id,
                                'attribute_value_ids': [(6, 0, list(value_ids))],
                                'active': tmpl_id.active,
                                'state': tmpl_id.state,
                            })
                            if len(variants_to_create) > 1000:
                                raise UserError(_(
                                    'The number of variants to generate is too high.'
                                    'You should either not generate variants for each combination or generate them on demand from the sales order. '
                                    'To do so, open the form view of attributes and change the mode of *Create Variants*.'))

            # Check existing variants if any needs to be activated or unlinked.
            # - if the product is not active and has valid attributes and attribute values, it
            #   should be activated
            # - if the product does not have valid attributes or attribute values, it should be
            #   deleted
            valid_value_ids = tmpl_id.valid_product_attribute_value_wnva_ids
            valid_attribute_ids = tmpl_id.valid_product_attribute_wnva_ids
            seen_attributes = set(
                p.attribute_value_ids for p in tmpl_id.product_variant_ids if p.active)
            for product_id in tmpl_id.product_variant_ids:
                if product_id._has_valid_attributes(valid_attribute_ids, valid_value_ids):
                    if not product_id.active and product_id.attribute_value_ids not in seen_attributes:
                        variants_to_activate += product_id
                        seen_attributes.add(product_id.attribute_value_ids)
                else:
                    variants_to_unlink += product_id

            if variants_to_activate:
                variants_to_activate.write({'active': True})

            # create new products
            price_to_create = []
            if variants_to_create:
                product_id = product.create(variants_to_create)
                for line in product_id:
                    for price in price_ids:
                        price_vals = {    
                            'base_price': price.base_price,
                            'currency': price.currency.id,
                            'uom_id': price.uom_id.id,
                            'discount': price.discount,
                            'price_txt': price.price_txt,
                            'minimum': price.minimum,
                            'multiple': price.multiple,
                            'start_date': price.start_date,
                            'end_date': price.end_date,
                            'preferred': price.preferred,
                            'desc': price.desc,
                            'product_tmpl_id': tmpl_id.id,
                            'vendor_id' : tmpl_id.vendor_id.id,
                            'product_id':line.id,
                            'state':price.state,
                            'template_price_id':price.id,
                            'temp_status':True
                            }
                        vp_price = line.vendor_price_ids.create(price_vals)


            # Avoid access errors in case the products is shared amongst companies but the underlying
            # objects are not. If unlink fails because of an AccessError (e.g. while recomputing
            # fields), the 'write' call will fail as well for the same reason since the field has
            # been set to recompute.
            if variants_to_unlink:
                variants_to_unlink.check_access_rights('unlink')
                variants_to_unlink.check_access_rule('unlink')
                variants_to_unlink.check_access_rights('write')
                variants_to_unlink.check_access_rule('write')
                variants_to_unlink = variants_to_unlink.sudo()
            # unlink or inactive product
            # try in batch first because it is much faster
            try:
                with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                    variants_to_unlink.unlink()
            except Exception:
                # fall back to one by one if batch is not possible
                for variant in variants_to_unlink:
                    try:
                        with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                            variant.unlink()
                    # We catch all kind of exception to be sure that the operation doesn't fail.
                    except Exception:
                        # Note: this can still fail if something is preventing from archiving.
                        # This is the case from existing stock reordering rules.
                        variant.write({'active': False})

        # prefetched o2m have to be reloaded (because of active_test)
        # (eg. product.template: product_variant_ids)
        # We can't rely on existing invalidate_cache because of the savepoint.
        self.invalidate_cache()
        return True

    def has_dynamic_attributes(self):
        """Return whether this `product.template` has at least one dynamic
        attribute.

        :return: True if at least one dynamic attribute, False otherwise
        :rtype: bool
        """
        self.ensure_one()
        return any(a.create_variant == 'dynamic' for a in self._get_valid_product_attributes())

    @api.multi
    def _compute_valid_attributes(self):
        """A product template attribute line is considered valid if it has at
        least one possible value.

        Those with only one value are considered valid, even though they should
        not appear on the configurator itself (unless they have an is_custom
        value to input), indeed single value attributes can be used to filter
        products among others based on that attribute/value.

        A product attribute value is considered valid for a template if it is
        defined on a product template attribute line.

        A product attribute is considered valid for a template if it
        has at least one possible value set on the template.

        For what is considered an archived variant, see `_has_valid_attributes`.
        """
        # prefetch
        self.mapped('attribute_line_ids.value_ids.id')
        self.mapped('attribute_line_ids.attribute_id.create_variant')

        for record in self:
            record.valid_product_template_attribute_line_ids = record.attribute_line_ids.filtered(
                lambda ptal: ptal.value_ids)
            record.valid_product_template_attribute_line_wnva_ids = record.valid_product_template_attribute_line_ids._without_no_variant_attributes()

            record.valid_product_attribute_value_ids = record.valid_product_template_attribute_line_ids.mapped(
                'value_ids')
            record.valid_product_attribute_value_wnva_ids = record.valid_product_template_attribute_line_wnva_ids.mapped(
                'value_ids')

            record.valid_product_attribute_ids = record.valid_product_template_attribute_line_ids.mapped(
                'attribute_id')
            record.valid_product_attribute_wnva_ids = record.valid_product_template_attribute_line_wnva_ids.mapped(
                'attribute_id')

    @api.multi
    def _compute_valid_archived_variant_ids(self):
        """This compute is done outside of `_compute_valid_attributes` because
        it is often not needed, and it can be very bad on performance."""
        archived_variants = self.env['vendor.product.product'].search(
            [('product_tmpl_id', 'in', self.ids), ('active', '=', False)])
        for record in self:
            valid_value_ids = record.valid_product_attribute_value_wnva_ids
            valid_attribute_ids = record.valid_product_attribute_wnva_ids

            record.valid_archived_variant_ids = archived_variants.filtered(
                lambda v: v.product_tmpl_id == record and v._has_valid_attributes(
                    valid_attribute_ids, valid_value_ids)
            )

    @api.multi
    def _compute_valid_existing_variant_ids(self):
        """This compute is done outside of `_compute_valid_attributes` because
        it is often not needed, and it can be very bad on performance."""
        existing_variants = self.env['vendor.product.product'].search(
            [('product_tmpl_id', 'in', self.ids), ('active', '=', True)])
        for record in self:

            valid_value_ids = record.valid_product_attribute_value_wnva_ids
            valid_attribute_ids = record.valid_product_attribute_wnva_ids

            record.valid_existing_variant_ids = existing_variants.filtered(
                lambda v: v.product_tmpl_id == record and v._has_valid_attributes(
                    valid_attribute_ids, valid_value_ids)
            )

    @api.multi
    def _get_valid_product_template_attribute_lines(self):
        """deprecated, use `valid_product_template_attribute_line_ids`"""
        self.ensure_one()
        return self.valid_product_template_attribute_line_ids

    @api.multi
    def _get_valid_product_attributes(self):
        """deprecated, use `valid_product_attribute_ids`"""
        self.ensure_one()
        return self.valid_product_attribute_ids

    @api.multi
    def _get_valid_product_attribute_values(self):
        """deprecated, use `valid_product_attribute_value_ids`"""
        self.ensure_one()
        return self.valid_product_attribute_value_ids

    @api.multi
    def _get_possible_variants(self, parent_combination=None):
        """Return the existing variants that are possible.

        For dynamic attributes, it will only return the variants that have been
        created already. For no_variant attributes, it will return an empty
        recordset because the variants themselves are not a full combination.
        If there are a lot of variants, this method might be slow. Even if there
        aren't too many variants, for performance reasons, do not call this
        method in a loop over the product templates.

        Therefore this method has a very restricted reasonable use case and you
        should strongly consider doing things differently if you consider using
        this method.

        :param parent_combination: combination from which `self` is an
            optional or accessory product.
        :type parent_combination: recordset `vendor.product.template.attribute.value`

        :return: the existing variants that are possible.
        :rtype: recordset of `vendor.product.product`
        """
        self.ensure_one()
        return self.product_variant_ids.filtered(lambda p: p._is_variant_possible(parent_combination))

    @api.multi
    def get_filtered_variants(self, reference_product=None):
        """deprecated, use _get_possible_variants instead"""
        self.ensure_one()

        parent_combination = self.env['vendor.product.template.attribute.value']

        if reference_product:
            # append the reference_product if provided
            parent_combination |= reference_product.product.product_template_attribute_value_ids
            if reference_product.env.context.get('no_variant_attribute_values'):
                # Add "no_variant" attribute values' exclusions
                # They are kept in the context since they are not linked to this product variant
                parent_combination |= reference_product.env.context.get(
                    'no_variant_attribute_values')
        return self._get_possible_variants(parent_combination)

    @api.multi
    def _get_attribute_exclusions(self, parent_combination=None):
        """Return the list of attribute exclusions of a product.

        :param parent_combination: the combination from which
            `self` is an optional or accessory product. Indeed exclusions
            rules on one product can concern another product.
        :type parent_combination: recordset `vendor.product.template.attribute.value`

        :return: dict of exclusions
            - exclusions: from this product itself
            - parent_combination: ids of the given parent_combination
            - parent_exclusions: from the parent_combination
            - archived_combinations: deprecated
            - existing_combinations: deprecated
            - has_dynamic_attributes: deprecated
            - no_variant_product_template_attribute_value_ids: deprecated
        """
        self.ensure_one()
        parent_combination = parent_combination or self.env['vendor.product.template.attribute.value']
        return {
            'exclusions': self._get_own_attribute_exclusions(),
            'parent_exclusions': self._get_parent_attribute_exclusions(parent_combination),
            'parent_combination': parent_combination.ids,
            'archived_combinations': [],
            'has_dynamic_attributes': self.has_dynamic_attributes(),
            'existing_combinations': [],
            'no_variant_product_template_attribute_value_ids': [],
        }

    @api.multi
    def _get_own_attribute_exclusions(self):
        """Get exclusions coming from the current template.

        Dictionnary, each ptav is a key, and for each of them the value is
        an array with the other ptav that they exclude (empty if no exclusion).
        """
        self.ensure_one()
        product_template_attribute_values = self._get_valid_product_template_attribute_lines(
        ).mapped('product_template_value_ids')
        return {
            ptav.id: [
                value_id
                for filter_line in ptav.exclude_for.filtered(
                    lambda filter_line: filter_line.product_tmpl_id == self
                ) for value_id in filter_line.value_ids.ids
            ]
            for ptav in product_template_attribute_values
        }

    @api.multi
    def _get_parent_attribute_exclusions(self, parent_combination):
        """Get exclusions coming from the parent combination.

        Array, each element is a ptav that is excluded because of the parent.
        """
        self.ensure_one()
        if not parent_combination:
            return []

        # Search for exclusions without attribute value. This means that the template is not
        # compatible with the parent combination. If such an exclusion is found, it means that all
        # attribute values are excluded.
        if parent_combination:
            exclusions = self.env['vendor.product.template.attribute.exclusion'].search([
                ('product_tmpl_id', '=', self.id),
                ('value_ids', '=', False),
                ('product_template_attribute_value_id',
                 'in', parent_combination.ids),
            ], limit=1)
            if exclusions:
                return self.mapped('attribute_line_ids.product_template_value_ids').ids

        return [
            value_id
            for filter_line in parent_combination.mapped('exclude_for').filtered(
                lambda filter_line: filter_line.product_tmpl_id == self
            ) for value_id in filter_line.value_ids.ids
        ]

    @api.multi
    def _get_archived_combinations(self):
        """Deprecated"""
        self.ensure_one()
        return [archived_variant.product_template_attribute_value_ids.ids
                for archived_variant in self.valid_archived_variant_ids]

    @api.multi
    def _get_existing_combinations(self):
        """Deprecated"""
        self.ensure_one()
        return [variant.product_template_attribute_value_ids.ids
                for variant in self.valid_existing_variant_ids]

    @api.multi
    def _get_no_variant_product_template_attribute_values(self):
        """Deprecated"""
        self.ensure_one()
        product_template_attribute_values = self._get_valid_product_template_attribute_lines(
        ).mapped('product_template_value_ids')
        return product_template_attribute_values.filtered(
            lambda v: v.attribute_id.create_variant == 'no_variant'
        ).ids

    @api.multi
    def _is_combination_possible(self, combination, parent_combination=None):
        """
        The combination is possible if it is not excluded by any rule
        coming from the current template, not excluded by any rule from the
        parent_combination (if given), and there should not be any archived
        variant with the exact same combination.

        If the template does not have any dynamic attribute, the combination
        is also not possible if the matching variant has been deleted.

        Moreover the attributes of the combination must excatly match the
        attributes allowed on the template.

        :param combination: the combination to check for possibility
        :type combination: recordset `vendor.product.template.attribute.value`

        :param parent_combination: combination from which `self` is an
            optional or accessory product.
        :type parent_combination: recordset `vendor.product.template.attribute.value`

        :return: whether the combination is possible
        :rtype: bool
        """
        self.ensure_one()

        if len(combination) != len(self.valid_product_template_attribute_line_ids):
            # number of attribute values passed is different than the
            # configuration of attributes on the template
            return False

        if self.valid_product_attribute_ids != combination.mapped('attribute_id'):
            # combination has different attributes than the ones configured on the template
            return False

        if self.valid_product_attribute_value_ids < combination.mapped('product_attribute_value_id'):
            # combination has different values than the ones configured on the template
            return False

        variant = self._get_variant_for_combination(combination)

        if self.has_dynamic_attributes():
            if variant and not variant.active:
                # dynamic and the variant has been archived
                return False
        else:
            if not variant or not variant.active:
                # not dynamic, the variant has been archived or deleted
                return False

        exclusions = self._get_own_attribute_exclusions()
        if exclusions:
            # exclude if the current value is in an exclusion,
            # and the value excluding it is also in the combination
            for ptav in combination:
                for exclusion in exclusions.get(ptav.id):
                    if exclusion in combination.ids:
                        return False

        parent_exclusions = self._get_parent_attribute_exclusions(
            parent_combination)
        if parent_exclusions:
            for exclusion in parent_exclusions:
                if exclusion in combination.ids:
                    return False

        return True

    @api.multi
    def _get_variant_for_combination(self, combination):
        """Get the variant matching the combination.

        All of the values in combination must be present in the variant, and the
        variant should not have more attributes. Ignore the attributes that are
        not supposed to create variants.

        :param combination: recordset of `vendor.product.template.attribute.value`

        :return: the variant if found, else empty
        :rtype: recordset `vendor.product.product`
        """
        self.ensure_one()

        filtered_combination = combination._without_no_variant_attributes()
        attribute_values = filtered_combination.mapped(
            'product_attribute_value_id')
        return self.env['vendor.product.product'].browse(self._get_variant_id_for_combination(attribute_values))

    @api.multi
    @tools.ormcache('self', 'attribute_values')
    def _get_variant_id_for_combination(self, attribute_values):
        """See `_get_variant_for_combination`. This method returns an ID
        so it can be cached."""
        self.ensure_one()
        # If there are a lot of variants on this template, it is much faster to
        # build a query than using the existing o2m.
        domain = [('product_tmpl_id', '=', self.id)]
        for pav in attribute_values:
            domain = expression.AND(
                [[('attribute_value_ids', 'in', pav.id)], domain])

        res = self.env['vendor.product.product'].with_context(
            active_test=False).search(domain, order='active DESC')

        # The domain above is checking for the `vendor.product.attr.value`, but we
        # need to make sure it's the same `vendor.product.template.attribute.value`.
        # Also there should theorically be only 0 or 1 but an existing database
        # might not be consistent so we need to make sure to take max 1.
        return res.filtered(
            lambda v: v.attribute_value_ids == attribute_values
        )[:1].id

    @api.multi
    @tools.ormcache('self')
    def _get_first_possible_variant_id(self):
        """See `_create_first_product_variant`. This method returns an ID
        so it can be cached."""
        self.ensure_one()
        return self._create_first_product_variant().id

    @api.multi
    def _get_first_possible_combination(self, parent_combination=None, necessary_values=None):
        """See `_get_possible_combinations` (one iteration).

        This method return the same result (empty recordset) if no
        combination is possible at all which would be considered a negative
        result, or if there are no attribute lines on the template in which
        case the "empty combination" is actually a possible combination.
        Therefore the result of this method when empty should be tested
        with `_is_combination_possible` if it's important to know if the
        resulting empty combination is actually possible or not.
        """
        return next(self._get_possible_combinations(parent_combination, necessary_values), self.env['vendor.product.template.attribute.value'])

    @api.multi
    def _get_possible_combinations(self, parent_combination=None, necessary_values=None):
        """Generator returning combinations that are possible, following the
        sequence of attributes and values.

        See `_is_combination_possible` for what is a possible combination.

        When encountering an impossible combination, try to change the value
        of attributes by starting with the further regarding their sequences.

        Ignore attributes that have no values.

        :param parent_combination: combination from which `self` is an
            optional or accessory product.
        :type parent_combination: recordset `vendor.product.template.attribute.value`

        :param necessary_values: values that must be in the returned combination
        :type necessary_values: recordset of `vendor.product.template.attribute.value`

        :return: the possible combinations
        :rtype: generator of recordset of `vendor.product.template.attribute.value`
        """
        self.ensure_one()

        if not self.active:
            return _("The product template is archived so no combination is possible.")

        necessary_values = necessary_values or self.env['vendor.product.template.attribute.value']
        necessary_attributes = necessary_values.mapped('attribute_id')
        ptal_stack = [self.valid_product_template_attribute_line_ids.filtered(
            lambda ptal: ptal.attribute_id not in necessary_attributes)]
        combination_stack = [necessary_values]

        # keep going while we have attribute lines to test
        while len(ptal_stack):
            attribute_lines = ptal_stack.pop()
            combination = combination_stack.pop()

            if not attribute_lines:
                # full combination, if it's possible return it, otherwise skip it
                if self._is_combination_possible(combination, parent_combination):
                    yield(combination)
            else:
                # we have remaining attribute lines to consider
                for ptav in reversed(attribute_lines[0].product_template_value_ids):
                    ptal_stack.append(attribute_lines[1:])
                    combination_stack.append(combination + ptav)

        return _("There are no remaining possible combination.")

    @api.multi
    def _get_closest_possible_combination(self, combination):
        """See `_get_closest_possible_combinations` (one iteration).

        This method return the same result (empty recordset) if no
        combination is possible at all which would be considered a negative
        result, or if there are no attribute lines on the template in which
        case the "empty combination" is actually a possible combination.
        Therefore the result of this method when empty should be tested
        with `_is_combination_possible` if it's important to know if the
        resulting empty combination is actually possible or not.
        """
        return next(self._get_closest_possible_combinations(combination), self.env['vendor.product.template.attribute.value'])

    @api.multi
    def _get_closest_possible_combinations(self, combination):
        """Generator returning the possible combinations that are the closest to
        the given combination.

        If the given combination is incomplete, try to complete it.

        If the given combination is invalid, try to remove values from it before
        completing it.

        :param combination: the values to include if they are possible
        :type combination: recordset `vendor.product.template.attribute.value`

        :return: the possible combinations that are including as much
            elements as possible from the given combination.
        :rtype: generator of recordset of vendor.product.template.attribute.value
        """
        while True:
            res = self._get_possible_combinations(necessary_values=combination)
            try:
                # If there is at least one result for the given combination
                # we consider that combination set, and we yield all the
                # possible combinations for it.
                yield(next(res))
                for cur in res:
                    yield(cur)
                return _("There are no remaining closest combination.")
            except StopIteration:
                # There are no results for the given combination, we try to
                # progressively remove values from it.
                if not combination:
                    return _("There are no possible combination.")
                combination = combination[:-1]

    def update_products_variants(self):
        product_variant = {}

        # purchasing part
        product_variant.update({
            'vendor_id': self.vendor_id.id,
            'vendor_description': self.vendor_description,
            'uom_ids': self.uom_ids,
            'delivery_warning': self.delivery_warning,
            'invoice_warning': self.invoice_warning,
            'purchasing_comments': self.purchasing_comments,
            'state': 'active',
        })

        # shipping
        product_variant.update({
            'dim1': self.dim1,
            'dim2': self.dim2,
            'dim3': self.dim3,
            'each_additional3': self.each_additional3,
            'cross_section': self.cross_section,
            'volume': self.volume,
            'shipping_comments': self.shipping_comments,
            'freight_bill_warn': self.freight_bill_warn,
            'truckload_qty': self.truckload_qty,
            'nmfc_code': self.nmfc_code.id,
            'first_unit': self.first_unit,
            'each_additional': self.each_additional,
            'hts_code': self.hts_code.id,
            'container_qty': self.container_qty
        })

        # # Pricing
        # product_variant.update({'vendor_price_ids': [(6, 0, self.vendor_price_ids.ids)]})
        if product_variant:
            for product in self.product_variant_ids:
                product.write(product_variant)
        return True
