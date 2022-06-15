import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.tools import pycompat


class VendorProductProduct(models.Model):
    _name = "vendor.product.product"
    _description = "Product"
    _inherits = {'vendor.product.template': 'product_tmpl_id'}
    _order = 'stock_id, name, id'
    _rec_name = 'complete_name'
    
    complete_name = fields.Char(compute="get_vendor_product_complete_name", string="Vendor Product", store=True)

    @api.depends('stock_id','attribute_value_ids')
    def get_vendor_product_complete_name(self):
        for line in self:
            code = ''
            if line.stock_id:
                if line.stock_id[0:1] != '[':
                    code = '[' + str(line.stock_id)
                else:
                    code = line.stock_id
                if line.stock_id[len(line.stock_id) - 1:len(line.stock_id)] != ']':
                    code += '] '
            code1 = ''
            if line.attribute_value_ids:
                seq = []
                seq_attr = {}
                for line1 in line.product_tmpl_id.attribute_line_ids:
                    seq.append(line1.sequence)
                    seq_attr[line1.sequence] = line1.value_ids
                seq.sort()
                for sq in seq:
                    code1 += line.get_code(seq_attr[sq])
            if code1:
                code1 = "%s"%(code1)
            line.complete_name = code + (line.name or line.product_tmpl_id.name) + code1
        return True

    stock_id = fields.Char('Vendor Stock ID')
    active = fields.Boolean(
        'Active',
        help="If unchecked, it will allow you to hide the product without removing it.")
    product_tmpl_id = fields.Many2one(
        'vendor.product.template', 'Template',
        auto_join=True, index=True, ondelete="cascade", required=True)
    attribute_value_ids = fields.Many2many(
        'vendor.product.attr.value', string='Attribute Values', ondelete='restrict')
    product_template_attribute_value_ids = fields.Many2many(
        'vendor.product.template.attribute.value', string='Template Attribute Values', compute="_compute_product_template_attribute_value_ids")
    # image: all image fields are base64 encoded and PIL-supported
    image_variant = fields.Binary(
        "Variant Image", attachment=True,
        help="This field holds the image used as image for the product variant, limited to 1024x1024px.")
    image = fields.Binary(
        "Big-sized image", compute='_compute_images', inverse='_set_image',
        help="Image of the product variant (Big-sized image of product template if false). It is automatically "
             "resized as a 1024x1024px image, with aspect ratio preserved.")
    image_small = fields.Binary(
        "Small-sized image", compute='_compute_images', inverse='_set_image_small',
        help="Image of the product variant (Small-sized image of product template if false).")
    image_medium = fields.Binary(
        "Medium-sized image", compute='_compute_images', inverse='_set_image_medium',
        help="Image of the product variant (Medium-sized image of product template if false).")
    is_product_variant = fields.Boolean(compute='_compute_is_product_variant')
    task_count = fields.Integer(string='Tasks')
    project_count = fields.Integer(string='Projects')
    document_count = fields.Integer(string='Documents')
    state = fields.Selection([('draft', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string="Stage", default='draft')
    dim1 = fields.Float(string='Dimension 1')
    dim2 = fields.Float(string='Dimension 2')
    dim3 = fields.Float(string='Dimension 3')
    each_additional3 = fields.Float(string='Each Additional 3')
    cross_section = fields.Float(string='Cross Section')
    volume = fields.Float(string='Volume')
    first_unit = fields.Float(string="First Unit")
    each_additional = fields.Float(string="Each Additional")
    nmfc_code = fields.Many2one('nmfc.class', string="NMFC Code")
    nmfc_desc = fields.Char(related='nmfc_code.description', string='NMFC Description')
    nmfc_class = fields.Char(related='nmfc_code.nmfc_class', string='NMFC Class')
    truckload_qty = fields.Float(string='Truckload Quantity')
    hts_code = fields.Many2one('hts.description', string='HTS Code')
    hts_desc = fields.Char(related='hts_code.description', string='HTS Description')
    container_qty = fields.Char(string='Container Quantity')
    freight_bill_warn = fields.Char(string='Freight Bill Warning')
    shipping_comments = fields.Text(string='Shipping Comments')
    vendor_price_ids = fields.One2many('vendor.price', 'product_id', 'Create a Vendor Product Price')
    equivalents_ids = fields.One2many('vendor.product.equivalents', 'vendor_prod_id', string='Create an Equivalent')
    temp_preferred = fields.Boolean(string='TPreferred')

    @api.onchange('vendor_price_ids')
    def _onchange_vendor_price_ids(self):
        update_default = False
        for data in self.vendor_price_ids:
            if data.temp_preferred:
                update_default = True
                break

        if update_default:
            for data in self.vendor_price_ids:
                if data.preferred and data.temp_preferred:
                    data.temp_preferred = False 
                    self.temp_preferred = True
                else:
                   data.preferred = False

    def reset_to_draft(self):
        self.active = False
        self.state = 'draft'

    def active_template(self):
        self.active = True
        self.state = 'active'

    def deactivate_template(self):
        self.active = False
        self.state = 'inactive'

    def product_documents(self):
        return

    def _compute_is_product_variant(self):
        for product in self:
            product.is_product_variant = True

    @api.one
    @api.depends('image_variant', 'product_tmpl_id.image')
    def _compute_images(self):
        if self._context.get('bin_size'):
            self.image_medium = self.image_variant
            self.image_small = self.image_variant
            self.image = self.image_variant
        else:
            resized_images = tools.image_get_resized_images(self.image_variant, return_big=True, avoid_resize_medium=True)
            self.image_medium = resized_images['image_medium']
            self.image_small = resized_images['image_small']
            self.image = resized_images['image']
        if not self.image_medium:
            self.image_medium = self.product_tmpl_id.image_medium
        if not self.image_small:
            self.image_small = self.product_tmpl_id.image_small
        if not self.image:
            self.image = self.product_tmpl_id.image

    @api.one
    def _set_image(self):
        self._set_image_value(self.image)

    @api.one
    def _set_image_medium(self):
        self._set_image_value(self.image_medium)

    @api.one
    def _set_image_small(self):
        self._set_image_value(self.image_small)

    @api.one
    def _set_image_value(self, value):
        if isinstance(value, pycompat.text_type):
            value = value.encode('ascii')
        image = tools.image_resize_image_big(value)

        # This is needed because when there is only one variant, the user
        # doesn't know there is a difference between template and variant, he
        # expects both images to be the same.
        if self.product_tmpl_id.image and self.product_variant_count > 1:
            self.image_variant = image
        else:
            self.image_variant = False
            self.product_tmpl_id.image = image

    @api.depends('product_tmpl_id', 'attribute_value_ids')
    def _compute_product_template_attribute_value_ids(self):
        # Fetch and pre-map the values first for performance. It assumes there
        # won't be too many values, but there might be a lot of products.
        values = self.env['vendor.product.template.attribute.value'].search([
            ('product_tmpl_id', 'in', self.mapped('product_tmpl_id').ids),
            ('product_attribute_value_id', 'in', self.mapped('attribute_value_ids').ids),
        ])

        values_per_template = {}
        for ptav in values:
            pt_id = ptav.product_tmpl_id.id
            if pt_id not in values_per_template:
                values_per_template[pt_id] = {}
            values_per_template[pt_id][ptav.product_attribute_value_id.id] = ptav

        for product in self:
            product.product_template_attribute_value_ids = self.env['vendor.product.template.attribute.value']
            for pav in product.attribute_value_ids:
                if product.product_tmpl_id.id not in values_per_template or pav.id not in values_per_template[product.product_tmpl_id.id]:
                    _logger.warning("A matching vendor.product.template.attribute.value was not found for the vendor.product.attr.value #%s on the template #%s" % (pav.id, product.product_tmpl_id.id))
                else:
                    product.product_template_attribute_value_ids += values_per_template[product.product_tmpl_id.id][pav.id]

    @api.constrains('attribute_value_ids')
    def _check_attribute_value_ids(self):
        for product in self:
            attributes = self.env['vendor.product.attribute']
            for value in product.attribute_value_ids:
                if value.attribute_id in attributes:
                    raise ValidationError(_('Error! It is not allowed to choose more than one value for a given attribute.'))
                if value.attribute_id.create_variant == 'always':
                    attributes |= value.attribute_id
        return True

    @api.model_create_multi
    def create(self, vals_list):
        products = super(VendorProductProduct, self.with_context(create_product_product=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants
        self.clear_caches()
        self.env['vendor.product.template'].invalidate_cache(
            fnames=[
                'valid_archived_variant_ids',
                'valid_existing_variant_ids',
                'product_variant_ids',
                'product_variant_id',
                'product_variant_count'
            ],
            ids=products.mapped('product_tmpl_id').ids
        )
        return products

    @api.multi
    def write(self, vals):
        ''' Store the standard price change in order to be able to retrieve the cost of a product for a given date'''
        res = super(VendorProductProduct, self).write(vals)
        if 'attribute_value_ids' in vals:
            # `_get_variant_id_for_combination` depends on `attribute_value_ids`
            self.clear_caches()
        if 'active' in vals:
            # prefetched o2m have to be reloaded (because of active_test)
            # (eg. vendor.product.template: product_variant_ids)
            self.invalidate_cache()
            # `_get_first_possible_variant_id` depends on variants active state
            self.clear_caches()
        if vals.get('vendor_price_ids') or vals.get('equivalents_ids'):
            if self.vendor_price_ids and self.equivalents_ids:
                for price in self.vendor_price_ids:
                    if price.state == 'active':
                        for equivalent in self.equivalents_ids:
                            if equivalent.vendor_prod_uom == price.uom_id:
                                prod_min = False
                                prod_price = False
                                minimum = False
                                price_value = False
                                greater = min(equivalent.product_qty, equivalent.vendor_prod_qty)
                                lower = max(equivalent.product_qty, equivalent.vendor_prod_qty)
                                unit_value = lower/greater
                                if equivalent.vendor_prod_qty < equivalent.product_qty:
                                    minimum = price.minimum
                                    price_value = price.price
                                    prod_min = round(price.minimum * unit_value,2)
                                    # prod_mult = round(price.multiple / equivalent.vendor_prod_qty, 2)
                                    prod_price = round(price.price / equivalent.product_qty, 2)
                                if equivalent.vendor_prod_qty > equivalent.product_qty:
                                    minimum = price.minimum
                                    price_value = price.price
                                    prod_min = round(price.minimum / unit_value,2)
                                    prod_price = round(price.price * unit_value,2)
                                source_vals = {
                                    'vendor_id': equivalent.vendor_id.id,
                                    'vendor_product_id': equivalent.vendor_prod_id.id,
                                    'vendor_desc': equivalent.vendor_prod_desc,
                                    'vendor_qty': equivalent.vendor_prod_qty,
                                    'uom_id': equivalent.vendor_prod_uom.id,
                                    'price': price_value,
                                    'currency_id': price.currency.id,
                                    'minimum': minimum,
                                    'multiple': price.multiple,
                                    'effective': price.start_date,
                                    'expiration': price.end_date,
                                    'days': price.days,
                                    'company_id': equivalent.company_id.id,
                                    'product_id': equivalent.product_id.id,
                                    'desc': '',
                                    'qty': equivalent.product_qty,
                                    'product_unit': equivalent.uom_id.id,
                                    'lst_price': prod_price,
                                    'product_currency': equivalent.product_id.currency_id.id,
                                    'product_minimum': prod_min,
                                    'product_multiple': price.multiple,
                                    'product_effective': price.start_date,
                                    'product_expiration': price.end_date,
                                    'ship_days': price.days,
                                    'vendor_price_id': price.id,
                                    'equivalents_id': equivalent.id,
                                }
                                source = self.env['product.sources'].search([('vendor_price_id', '=', price.id), ('equivalents_id', '=', equivalent.id)])
                                if source:
                                    source.write(source_vals)
                                else:
                                    self.env['product.sources'].create(source_vals)                    
        return res

    @api.multi
    def unlink(self):
        unlink_products = self.env['vendor.product.product']
        unlink_templates = self.env['vendor.product.template']
        for product in self:
            # Check if product still exists, in case it has been unlinked by unlinking its template
            if not product.exists():
                continue
            # Check if the product is last product of this template...
            other_products = self.search([('product_tmpl_id', '=', product.product_tmpl_id.id), ('id', '!=', product.id)])
            # ... and do not delete product template if it's configured to be created "on demand"
            if not other_products and not product.product_tmpl_id.has_dynamic_attributes():
                unlink_templates |= product.product_tmpl_id
            unlink_products |= product
        res = super(VendorProductProduct, unlink_products).unlink()
        # delete templates after calling super, as deleting template could lead to deleting
        # products due to ondelete='cascade'
        unlink_templates.unlink()
        # `_get_variant_id_for_combination` depends on existing variants
        self.clear_caches()
        return res

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # TDE FIXME: clean context / variant brol
        if default is None:
            default = {}
        if self._context.get('variant'):
            # if we copy a variant or create one, we keep the same template
            default['product_tmpl_id'] = self.product_tmpl_id.id
        elif 'name' not in default:
            default['name'] = self.name

        return super(VendorProductProduct, self).copy(default=default)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        return super(VendorProductProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = self._search(args + [('stock_id', operator, name)], limit=limit)
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, access_rights_uid=name_get_uid)
                    product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('stock_id', operator, name), ('name', operator, name)],
                    ['&', ('stock_id', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                product_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = self._search([('stock_id', '=', res.group(2))] + args, limit=limit, access_rights_uid=name_get_uid)
            # still no results, partner in context: search on supplier info as last hope to find something
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(product_ids).name_get()

    @api.model
    def view_header_get(self, view_id, view_type):
        res = super(VendorProductProduct, self).view_header_get(view_id, view_type)
        return res

    @api.multi
    def open_product_template(self):
        """ Utility method used to add an "Open Template" button in product views """
        self.ensure_one()
        return {'type': 'ir.actions.act_window',
                'res_model': 'vendor.product.template',
                'view_mode': 'form',
                'res_id': self.product_tmpl_id.id,
                'target': 'new'}

    @api.model
    def get_empty_list_help(self, help):
        self = self.with_context(
            empty_list_help_document_name=_("product"),
        )
        return super(VendorProductProduct, self).get_empty_list_help(help)

    def _has_valid_attributes(self, valid_attributes, valid_values):
        """ Check if a product has valid attributes. It is considered valid if:
            - it uses ALL valid attributes
            - it ONLY uses valid values
            We must make sure that all attributes are used to take into account the case where
            attributes would be added to the template.

            This method does not check if the combination is possible, it just
            checks if it has valid attributes and values. A possible combination
            is always valid, but a valid combination is not always possible.

            :param valid_attributes: a recordset of vendor.product.attribute
            :param valid_values: a recordset of vendor.product.attr.value
            :return: True if the attibutes and values are correct, False instead
        """
        self.ensure_one()
        values = self.attribute_value_ids
        attributes = values.mapped('attribute_id')
        if attributes != valid_attributes:
            return False
        for value in values:
            if value not in valid_values:
                return False
        return True

    @api.multi
    def _is_variant_possible(self, parent_combination=None):
        """Return whether the variant is possible based on its own combination,
        and optionally a parent combination.

        See `_is_combination_possible` for more information.

        This will always exclude variants for templates that have `no_variant`
        attributes because the variant itself will not be the full combination.

        :param parent_combination: combination from which `self` is an
            optional or accessory product.
        :type parent_combination: recordset `vendor.product.template.attribute.value`

        :return: ẁhether the variant is possible based on its own combination
        :rtype: bool
        """
        self.ensure_one()
        return self.product_tmpl_id._is_combination_possible(self.product_template_attribute_value_ids, parent_combination=parent_combination)

    def get_code(self, values):
        code = ''
        attr_obj = self.env['vendor.product.template.attr.line']
        for attr in self.attribute_value_ids:
            if attr in values:
                variant_id = attr_obj.search([('product_tmpl_id','=',self.product_tmpl_id.id),('attribute_id','=',attr.attribute_id.id)])
                if variant_id.before:
                    deff = len(variant_id.before)
                    if deff == 1:
                        if variant_id.before == "#":
                            code += str(' ')+attr.name
                        else:
                            code += variant_id.before+attr.name
                    elif deff > 1:
                        if variant_id.before[0] == "#" and variant_id.before[deff-1] == "#":
                            code += str(' ')+variant_id.before[1:deff-1]+str(' ')+attr.name
                        if variant_id.before[0] == "#" and variant_id.before[deff-1] != "#":
                            code += str(' ')+variant_id.before[1:deff]+attr.name
                        if variant_id.before[0] != "#" and variant_id.before[deff-1] == "#":
                            code +=variant_id.before[0:deff-1]+str(' ')+attr.name
                    if variant_id.after:
                        deff2 = len(variant_id.after)
                        if deff2 == 1:
                            if variant_id.after == "#":
                                code += str(' ') 
                            else:
                                code += variant_id.after
                        elif deff2 > 1:
                            if variant_id.after[0] == "#" and variant_id.after[deff2-1] == "#":
                                code += str(' ')+variant_id.after[1:deff2-1]+str(' ')
                            if variant_id.after[0] == "#" and variant_id.after[deff2-1] != "#":
                                code += str(' ')+variant_id.after[1:deff2]
                            if variant_id.after[0] != "#" and variant_id.after[deff2-1] == "#":
                                code +=variant_id.after[0:deff2-1]+str(' ')
                elif variant_id.after:
                    deff2 = len(variant_id.after)
                    if deff2 == 1:
                        if variant_id.after == "#":
                            code += str(' ')+attr.name
                        else:
                            code += variant_id.after+attr.name
                    elif deff2 > 1:
                        if variant_id.after[0] == "#" and variant_id.after[deff2-1] == "#":
                            code += str(' ')+variant_id.after[1:deff2-1]+str(' ')+attr.name
                        if variant_id.after[0] == "#" and variant_id.after[deff2-1] != "#":
                            code += str(' ')+variant_id.after[1:deff2]+attr.name
                        if variant_id.after[0] != "#" and variant_id.after[deff2-1] == "#":
                            code +=variant_id.after[0:deff2-1]+str(' ')+attr.name
                if not variant_id.after and not variant_id.before:
                    code += str(' ')+attr.name
        return code


class HtsDescription(models.Model):
    _name = "hts.description"
    _description = "Harmonized Tariff Schedule"
    _rec_name = "code"

    code = fields.Char(string='Code')
    description = fields.Char(string='Description')
