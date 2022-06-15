# -*- coding: utf-8 -*-
# Copyright 2018 Akili
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=False ,readonly=True, help="Pricelist for current sales order.")
    mail_sent = fields.Boolean(string='Email Sent', default=False)
    so_pdf = fields.Binary(string='Quotation', attachment=True)

    def get_total_of_shipment(self):
        return True

    def pay_to_shipment(self):
        return True

    def release_shipments(self):
        return True

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """ Add or set product quantity, add_qty can be negative """
        self.ensure_one()
        product_context = dict(self.env.context)
        product_context.setdefault('lang', self.sudo().partner_id.lang)
        SaleOrderLineSudo = self.env['sale.order.line'].sudo().with_context(product_context)

        try:
            if add_qty:
                add_qty = float(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = float(set_qty)
        except ValueError:
            set_qty = 0
        quantity = 0
        order_line = False
        # if self.state != 'draft':
        #     request.session['sale_order_id'] = None
        #     raise UserError(_('It is forbidden to modify a sales order which is not in draft status.'))
        if line_id is not False:
            order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]

        # Create line if no line with product_id can be located
        if not order_line:
            # change lang to get correct name of attributes/values
            product = self.env['product.product'].with_context(product_context).browse(int(product_id))

            if not product:
                raise UserError(_("The given product does not exist therefore it cannot be added to cart."))

            no_variant_attribute_values = kwargs.get('no_variant_attribute_values') or []
            received_no_variant_values = product.env['product.template.attribute.value'].browse([int(ptav['value']) for ptav in no_variant_attribute_values])
            received_combination = product.product_template_attribute_value_ids | received_no_variant_values
            product_template = product.product_tmpl_id

            # handle all cases where incorrect or incomplete data are received
            combination = product_template._get_closest_possible_combination(received_combination)

            # get or create (if dynamic) the correct variant
            product = product_template._create_product_variant(combination)

            if not product:
                raise UserError(_("The given combination does not exist therefore it cannot be added to cart."))

            product_id = product.id

            values = self._website_product_id_change(self.id, product_id, qty=1)

            # add no_variant attributes that were not received
            for ptav in combination.filtered(lambda ptav: ptav.attribute_id.create_variant == 'no_variant' and ptav not in received_no_variant_values):
                no_variant_attribute_values.append({
                    'value': ptav.id,
                    'attribute_name': ptav.attribute_id.name,
                    'attribute_value_name': ptav.name,
                })

            # save no_variant attributes values
            if no_variant_attribute_values:
                values['product_no_variant_attribute_value_ids'] = [
                    (6, 0, [int(attribute['value']) for attribute in no_variant_attribute_values])
                ]

            # add is_custom attribute values that were not received
            custom_values = kwargs.get('product_custom_attribute_values') or []
            received_custom_values = product.env['product.attribute.value'].browse([int(ptav['attribute_value_id']) for ptav in custom_values])

            for ptav in combination.filtered(lambda ptav: ptav.is_custom and ptav.product_attribute_value_id not in received_custom_values):
                custom_values.append({
                    'attribute_value_id': ptav.product_attribute_value_id.id,
                    'attribute_value_name': ptav.name,
                    'custom_value': '',
                })

            # save is_custom attributes values
            if custom_values:
                values['product_custom_attribute_value_ids'] = [(0, 0, {
                    'attribute_value_id': custom_value['attribute_value_id'],
                    'custom_value': custom_value['custom_value']
                }) for custom_value in custom_values]

            # create the line
            order_line = SaleOrderLineSudo.create(values)
            # Generate the description with everything. This is done after
            # creating because the following related fields have to be set:
            # - product_no_variant_attribute_value_ids
            # - product_custom_attribute_value_ids
            order_line.name = order_line.get_sale_order_line_multiline_description_sale(product)

            try:
                order_line._compute_tax_id()
            except ValidationError as e:
                # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
                _logger.debug("ValidationError occurs during tax compute. %s" % (e))
            if add_qty:
                add_qty -= 1

        # compute new quantity
        if set_qty:
            quantity = set_qty
        elif add_qty is not None:
            quantity = order_line.product_uom_qty + (add_qty or 0)

        # Remove zero of negative lines
        if quantity <= 0:
            order_line.unlink()
        else:
            # update line
            no_variant_attributes_price_extra = [ptav.price_extra for ptav in order_line.product_no_variant_attribute_value_ids]
            values = self.with_context(no_variant_attributes_price_extra=no_variant_attributes_price_extra)._website_product_id_change(self.id, product_id, qty=quantity)
            if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
                order = self.sudo().browse(self.id)
                product_context.update({
                    'partner': order.partner_id,
                    'quantity': quantity,
                    'date': order.date_order,
                    'pricelist': order.pricelist_id.id,
                    'force_company': order.company_id.id,
                })
                product = self.env['product.product'].with_context(product_context).browse(product_id)
                values['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                    order_line._get_display_price(product),
                    order_line.product_id.taxes_id,
                    order_line.tax_id,
                    self.company_id
                )

            order_line.write(values)

            # link a product to the sales order
            if kwargs.get('linked_line_id'):
                linked_line = SaleOrderLineSudo.browse(kwargs['linked_line_id'])
                order_line.write({
                    'linked_line_id': linked_line.id,
                    'name': order_line.name + "\n" + _("Option for:") + ' ' + linked_line.product_id.display_name,
                })
                linked_line.write({"name": linked_line.name + "\n" + _("Option:") + ' ' + order_line.product_id.display_name})

        option_lines = self.order_line.filtered(lambda l: l.linked_line_id.id == order_line.id)
        for option_line_id in option_lines:
            self._cart_update(option_line_id.product_id.id, option_line_id.id, add_qty, set_qty, **kwargs)

        return {'line_id': order_line.id, 'quantity': quantity, 'option_ids': list(set(option_lines.ids))}
        

    
    @api.one
    def get_document_id(self):
        code = 'Quotation' 
        code2 = 'Cart'
        if self.state in ['sale','done']:
            code = str(self.name) + ' ' + self.partner_id.name
        self.sale_code = code

        if self.state in ['draft']:
            self.sale_code = code2

    sale_code = fields.Char(compute=get_document_id, string="Sale Code") 
    priority = fields.Selection(
        [
        ('x', 'Estimate for future project'),
        ('xx', 'Plan to order soon'),
        ('xxx', 'Ready to order now')],
        string='Priority', default='xx')

    priority_d = fields.Selection(
        [(' ',' '),
        ('x', 'Estimate for future project'),
        ('xx', 'Plan to order soon'),
        ('xxx', 'Ready to order now')],
        string='Priority', default='xx')

    @api.onchange('priority')
    def get_priority_seletion(self):
        for rec in self:
            if rec.priority:
                if rec.priority == 'x':
                    rec.priority_d = 'x'
                elif rec.priority == 'xx':
                    rec.priority_d = 'xx'
                elif rec.priority == 'xxx':
                    rec.priority_d = 'xxx'
            else:
                rec.priority_d = ' '

    @api.depends('date_order', 'order_line.customer_lead')
    def _compute_commitment_date(self):
        """Compute the commitment date"""
        for order in self:
            dates_list = []
            order_datetime = fields.Datetime.from_string(order.date_order)
            # order.state = 'sent'
            for line in order.order_line.filtered(lambda x: x.state != 'cancel'):
                dt = order_datetime + timedelta(days=line.customer_lead or 0.0)
                dates_list.append(dt)
            if dates_list:
                commit_date = min(dates_list) if order.picking_policy == 'direct' else max(dates_list)
                order.commitment_date = fields.Datetime.to_string(commit_date)
     
    
    commitment_date = fields.Datetime(compute='_compute_commitment_date', string='Commitment Date', store=True,
                                      help="Date by which the products are sure to be delivered. This is "
                                           "a date that you can promise to the customer, based on the "
                                           "Product Lead Times.")
    # @api.multi
    # @api.depends('order_line')
    # def compute_review_category(self):
    #     for order in self:
    #         category_id = False
    #         vals = dict()
    #         for line in order.order_line:
    #             if not line.product_id.categ_id.review_category_id.id:
    #                 continue  # Skip if no review category available for SO line
    #             elif not line.product_id.categ_id.review_category_id.id in vals.keys():
    #                 vals[line.product_id.categ_id.review_category_id.id] = line.price_subtotal
    #             elif line.product_id.categ_id.review_category_id.id in vals.keys():
    #                 vals[line.product_id.categ_id.review_category_id.id] += line.price_subtotal
    #         # To find max price_subtotal for a category, we first sort it and
    #         # get first element
    #         if vals:
    #             category_id, _ = sorted(
    #                 vals.iteritems(), key=lambda k_v: (
    #                     k_v[1], k_v[0]), reverse=True)[0]
    #         order.review_category_id = category_id

    # review_category_id = fields.Many2one('review.categories', compute='compute_review_category', inverse='_set_category_id',
    #     string='Product Team', store=True, copy=False, domain=[('sales_team', '=', True)])

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])
        self.partner_id_char = self.partner_id.id
        
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment term
        - Invoice address
        - Delivery address
        """
        if not self.partner_id:
            self.update({
                'partner_contact_id':False,
                'partner_invoice_id':False,
                'partner_shipping_id':False,                
                'partner_contact_phone': False,
                'partner_invoice_addr1': False,
                'partner_ship_addr1': False,
                'payment_term_id': False,
                'fiscal_position_id': False,
            })
            return

        if self.partner_id.child_ids:
            addr = {'partner_contact_id': False,
                    'partner_invoice_id': False,
                    'partner_shipping_id': False,
                    'partner_contact_phone': False,
                    'partner_invoice_addr1': False,
                    'partner_ship_addr1': False
                    }
            # Auto Update default contact addresses in address field in quotation
            
            for rec in self.partner_id.child_ids:

                if rec.default_address and rec.type_extend == 'contact':
                    addr['partner_contact_id'] = rec.id

                    complete_address = ''
                    if rec.name:
                        complete_address += rec.name
                        if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.comp_name: 
                        complete_address += rec.comp_name
                        if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street: 
                        complete_address += rec.street
                        if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street2: 
                        complete_address += rec.street2
                        if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and not rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.zip and not rec.state_id : 
                        complete_address += rec.city + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and rec.zip and not rec.city : 
                        complete_address += rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and not rec.state_id and not rec.zip: 
                        complete_address += rec.city
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and not rec.city and not rec.zip: 
                        complete_address += rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.zip and not rec.city and not rec.state_id: 
                        complete_address += rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if self.company_id:
                        if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                            complete_address += ''
                        else:
                            complete_address += rec.country_id.name if rec.country_id else ''

                    addr['partner_contact_phone'] = str(complete_address)

                # Auto Update default Billing addresses in address field in quotation
                
                if rec.default_address and rec.type_extend == 'invoice':
                    addr['partner_invoice_id'] = rec.id

                    complete_address = ''
                    if rec.name:
                        complete_address += rec.name
                        if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.comp_name: 
                        complete_address += rec.comp_name
                        if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street: 
                        complete_address += rec.street
                        if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street2: 
                        complete_address += rec.street2
                        if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and not rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.zip and not rec.state_id : 
                        complete_address += rec.city + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and rec.zip and not rec.city : 
                        complete_address += rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and not rec.state_id and not rec.zip: 
                        complete_address += rec.city
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and not rec.city and not rec.zip: 
                        complete_address += rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.zip and not rec.city and not rec.state_id: 
                        complete_address += rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if self.company_id:
                        if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                            complete_address += ''
                        else:
                            complete_address += rec.country_id.name if rec.country_id else '' 

                    addr['partner_invoice_addr1'] = str(complete_address)

                # Auto Update default Shipping addresses in address field in quotation

                if rec.default_address and rec.type_extend == 'delivery':
                    addr['partner_shipping_id'] = rec.id

                    complete_address = ''
                    if rec.name:
                        complete_address += rec.name
                        if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.comp_name: 
                        complete_address += rec.comp_name
                        if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street: 
                        complete_address += rec.street
                        if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.street2: 
                        complete_address += rec.street2
                        if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.state_id and not rec.zip : 
                        complete_address += rec.city + ' ' + rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and rec.zip and not rec.state_id : 
                        complete_address += rec.city + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and rec.zip and not rec.city : 
                        complete_address += rec.state_id.code + ' ' + rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.city and not rec.state_id and not rec.zip: 
                        complete_address += rec.city
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.state_id and not rec.city and not rec.zip: 
                        complete_address += rec.state_id.code
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if rec.zip and not rec.city and not rec.state_id: 
                        complete_address += rec.zip
                        if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                            complete_address += '\n'
                    if self.company_id:
                        if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                            complete_address += ''
                        else:
                            complete_address += rec.country_id.name if rec.country_id else ''

                    addr['partner_ship_addr1'] = str(complete_address)

        valid_days = self.env['ir.config_parameter'].search([('key','=', 'quotation_valid_days')])
        date = datetime.now().date() + timedelta(days=int(valid_days.value))
        default_pricelist = self.env['product.pricelist'].search([],limit=1)
        if self.partner_id.child_ids: 
            values = {
                'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
                'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
                'partner_contact_id': addr['partner_contact_id'],
                'partner_invoice_id': addr['partner_invoice_id'],
                'partner_shipping_id': addr['partner_shipping_id'],

                'partner_contact_phone': addr['partner_contact_phone'],
                'partner_invoice_addr1': addr['partner_invoice_addr1'],
                'partner_ship_addr1': addr['partner_ship_addr1'],

                'carrier_id': self.partner_id.property_delivery_carrier_id or False,
                'backorder': self.partner_id.backorder or False,
                'validity_date':date.strftime('%Y-%m-%d'),
                'user_id': self.partner_id.user_id.id or self.env.uid,
            }
        else:
             values = {
                'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
                'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
                'partner_contact_id': False,
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'partner_contact_phone':False,
                'partner_invoice_addr1':False,
                'partner_ship_addr1':False,
                'carrier_id': self.partner_id.property_delivery_carrier_id or False,
                'backorder': self.partner_id.backorder or False,
                'validity_date':date.strftime('%Y-%m-%d'),
                'user_id': self.partner_id.user_id.id or self.env.uid
            }


                

        if self.env.user.company_id.sale_note:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.user.company_id.sale_note

        if self.partner_id.user_id:
            values['user_id'] = self.partner_id.user_id.id
        if self.partner_id.team_id:
            values['team_id'] = self.partner_id.team_id.id
        self.update(values)
    
    reviewed_by=fields.Many2one('res.users',string='Reviewer',track_visibility='onchange',copy=False,)
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', readonly=False, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]}, help="Invoice address for current sales order.")
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=False, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]}, help="Delivery address for current sales order.")
    partner_id_char  =   fields.Char()

    @api.multi
    @api.depends('partner_contact_id')
    def get_complete_contact_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])
        if self.partner_contact_id:
            for rec in self.partner_contact_id:
                complete_address = ''
                if rec.name:
                    complete_address += rec.name
                    if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.comp_name: 
                    complete_address += rec.comp_name
                    if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street: 
                    complete_address += rec.street
                    if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street2: 
                    complete_address += rec.street2
                    if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and not rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.zip and not rec.state_id : 
                    complete_address += rec.city + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and rec.zip and not rec.city : 
                    complete_address += rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and not rec.state_id and not rec.zip: 
                    complete_address += rec.city
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and not rec.city and not rec.zip: 
                    complete_address += rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.zip and not rec.city and not rec.state_id: 
                    complete_address += rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if self.company_id:
                    if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                        complete_address += ''
                    else:
                        complete_address += rec.country_id.name if rec.country_id else ''
            self.partner_contact_phone = str(complete_address)
        else:
            self.partner_contact_phone = False
        
    @api.multi
    @api.depends('partner_invoice_id')
    def get_complete_invoice_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])    
        if self.partner_invoice_id:
            for rec in self.partner_invoice_id:
                complete_address = ''
                if rec.name:
                    complete_address += rec.name
                    if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.comp_name: 
                    complete_address += rec.comp_name
                    if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street: 
                    complete_address += rec.street
                    if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street2: 
                    complete_address += rec.street2
                    if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and not rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.zip and not rec.state_id : 
                    complete_address += rec.city + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and rec.zip and not rec.city : 
                    complete_address += rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and not rec.state_id and not rec.zip: 
                    complete_address += rec.city
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and not rec.city and not rec.zip: 
                    complete_address += rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.zip and not rec.city and not rec.state_id: 
                    complete_address += rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if self.company_id:
                    if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                        complete_address += ''
                    else:
                        complete_address += rec.country_id.name if rec.country_id else '' if rec.country_id else ''
            self.partner_invoice_addr1 = str(complete_address)
        else:
            self.partner_invoice_addr1 = False

    @api.multi
    @api.depends('partner_shipping_id')
    def get_complete_shipping_address(self):
        company_object = self.env['res.company'].search([('id','=',self.company_id.id)])        
        if self.partner_shipping_id:
            for rec in self.partner_shipping_id:
                complete_address = ''
                if rec.name:
                    complete_address += rec.name
                    if any([rec.comp_name, rec.street, rec.street2, rec.city, rec.state_id, rec.zip, rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.comp_name: 
                    complete_address += rec.comp_name
                    if any([rec.street, rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street: 
                    complete_address += rec.street
                    if any([rec.street2, rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.street2: 
                    complete_address += rec.street2
                    if any([rec.city, rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.state_id and not rec.zip : 
                    complete_address += rec.city + ' ' + rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and rec.zip and not rec.state_id : 
                    complete_address += rec.city + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and rec.zip and not rec.city : 
                    complete_address += rec.state_id.code + ' ' + rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.city and not rec.state_id and not rec.zip: 
                    complete_address += rec.city
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.state_id and not rec.city and not rec.zip: 
                    complete_address += rec.state_id.code
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if rec.zip and not rec.city and not rec.state_id: 
                    complete_address += rec.zip
                    if any([rec.state_id, rec.zip ,rec.phone, rec.country_id]):
                        complete_address += '\n'
                if self.company_id:
                    if rec.country_id.name == self.company_id.country_id.name and company_object.same_as_country:
                        complete_address += ''
                    else:
                        complete_address += rec.country_id.name if rec.country_id else ''
            self.partner_ship_addr1 = str(complete_address)
        else:
            self.partner_ship_addr1 = False

   
    @api.multi
    def _action_confirm(self):
        if not self.partner_contact_phone:
            raise UserError(_('The Contact is invalid field.'))
        if not self.partner_invoice_addr1:
            raise UserError(_('The Billing is invalid field.'))
        if not self.partner_ship_addr1:
            raise UserError(_('The Shipping is invalid field.'))
        res = super(SaleOrder, self)._action_confirm()
        for so in self:
            so.invoice_shipping_on_delivery = all([not line.is_delivery for line in so.order_line])
        for so_line in self.order_line:
            if so_line.is_sale_lines :
                so_line.is_sale_lines = True
            else :
                so_line.is_sale_lines = True
        return res
    
    @api.one
    @api.depends('partner_contact_id')
    def compute_contact(self):
        if self.partner_contact_id.phone:
            # self.partner_contact_phone = self.partner_contact_id.phone
            self.contact_name = self.partner_contact_id.name

    @api.multi
    def add_follower_id(self, res_id, partner_id, model):
        followers_obj = self.env['mail.followers']
        follower_id = followers_obj.search(
            [('res_id', '=', res_id),('res_model', '=', model), ('partner_id', '=', partner_id)])
        reg = {
            'res_id': res_id,
            'res_model': model,
            'partner_id': partner_id, }

        if not follower_id:
            follower_id = followers_obj.create(reg)
        else:
            _logger.info(u'AddFollower: follower already exists')        


    @api.model
    def create(self, vals):
        if 'website_id' not in self._context:
            vals['state'] = 'sent'
        res = super(SaleOrder, self).create(vals)
        if res.partner_id and res.partner_id.id != 4:
            res.add_follower_id(res.id,res.partner_id.id,'sale.order')
        # res.onchange_partner_id()
        return res

    @api.multi
    def write(self,vals):
        vals['date_order'] = fields.datetime.now()
        res = super(SaleOrder, self).write(vals)
        if self.partner_id and self.partner_id.id != 4:
            self.add_follower_id(self.id,self.partner_id.id,'sale.order')
        return res

    @api.multi
    @api.depends('review_category_id')
    def compute_hide_button(self):
        for order in self:
            order.hide_button = self.env.user in order.review_category_id.user_ids


    contact_name = fields.Char()
    partner_contact_id = fields.Many2one('res.partner', string='Contact', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    partner_contact_addr2 = fields.Char()
    partner_invoice_addr2 = fields.Char()
    partner_ship_addr2 = fields.Char()
    stock_reserved = fields.Boolean("Stock Reserved", default=False, readonly=True)

    hide_button = fields.Boolean(compute='compute_hide_button')
    # quote_stage = fields.Selection([('draft', 'CREATE'), ('review', 'REVIEW'), ('revise', 'REVISE'), ('send', 'SEND'), ('accept', 'ACCEPT'),('schedule', 'SCHEDULE')  ],
    #     default='draft', track_visibility='onchange', readonly=True, copy=False)
    # sub_state2 = fields.Selection([('wait', 'WAIT'), ('schedule', 'SOLD'), ], default='wait',
    #                                track_visibility='onchange', readonly=True, copy=False)
    # sub_state3 = fields.Selection([('reserve', 'RESERVE'),('pack', 'Pack'), ('release', 'RELEASE'), ('ship', 'Ship'),('invoice','INVOICE'),('done','Done') ], default='pack',
        # track_visibility='onchange', readonly=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True, index=True, track_visibility='always', track_sequence=1, help="You can find a customer by its Name, TIN, Email or Internal Reference.")
    project_count = fields.Integer(string='Opportunities')
    task_count = fields.Integer(string='Tasks')
    opp_count = fields.Integer(string='Projects')
   

    @api.multi
    def action_view_opportunity(self):
        if self.opp_count > 0:
            action = self.env.ref('account_workflow.customer_opportunities_tree').read()[0]
            return action
        else:
            tree_view = self.env.ref('lead_process.crm_opportunity_tree_view')
            form_view = self.env.ref('crm.crm_case_form_view_oppor')
            kanban_view = self.env.ref('lead_process.crm_opportunity_kanban_view')
            graph_view = self.env.ref('crm.crm_lead_view_graph')
            pivot_view = self.env.ref('crm.crm_lead_view_pivot')
            calendar_view = self.env.ref('crm.crm_case_calendar_view_leads')
            return {
                'name': _('Opportunities'),
                'view_type': 'form',
                'res_model': 'crm.lead',
                'views': [
                            (tree_view.id,'tree'), (form_view.id,'form'), (kanban_view.id,'kanban'),
                            (graph_view.id,'graph'), (pivot_view.id,'pivot'), (calendar_view.id,'calendar')
                        ],
                'context': {'default_type': 'opportunity','create':False},
                'domain': [('partner_id', '=', self._context.get('active_id', False)),('type','=','opportunity')],
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

    review_category_id = fields.Many2one('crm.team', compute='compute_review_category', inverse='_set_category_id',
        string='Product Team', store=True, copy=False, domain=[('sales_team', '=', True)])
    partner_invoice_addr1 = fields.Text(compute='get_complete_invoice_address',)
    partner_ship_addr1 = fields.Text(compute='get_complete_shipping_address',)
    partner_contact_phone = fields.Text(compute='get_complete_contact_address', string="Contact")

    @api.multi
    @api.depends('order_line')
    def compute_review_category(self):
        for order in self:
            category_id = False
            vals = dict()
            for line in order.order_line:
                if not line.product_id.categ_id.review_category_id:
                    continue  # Skip if no review category available for SO line
                elif not line.product_id.categ_id.review_category_id.id in vals.keys():
                    vals[line.product_id.categ_id.review_category_id.id] = line.price_subtotal
                elif line.product_id.categ_id.review_category_id.id in vals.keys():
                    vals[line.product_id.categ_id.review_category_id.id] += line.price_subtotal
            # To find max price_subtotal for a category, we first sort it and
            # get first element
            if vals:
                category_sorted_list = [k for k in sorted(vals, key=vals.get, reverse=True)]
                category_id = category_sorted_list
            order.review_category_id = category_id and category_id[0] or False

    quote_stage = fields.Selection(
        [('draft', 'DRAFT'),
         ('review', 'REVIEW'),
         ('revise', 'REVISE'),
         ('send', 'SEND'),
         ('accept', 'ACCEPT'),
         ('order', 'ORDER'),
         ('cancel', 'CANCEL')], default='draft', track_visibility='onchange', readonly=True, copy=False, string="Stage")

    order_stage = fields.Selection(
        [('schedule', 'SCHEDULE'),
         ('sale', 'SALE'),
         ('cancel', 'CANCEL')], default='schedule', track_visibility='onchange', readonly=True, copy=False, string="Stage")

    sub_state3 = fields.Selection(
        [('assign', 'ASSIGN'),
         ('wait', 'WAIT'),
         ('pick', 'PICK'),
         ('pack', 'PACK'),
         ('unitize', 'UNITIZE'),
         ('release', 'RELEASE'),
         ('ship', 'SHIP'),
         ('invoice', 'INVOICE'),
         ('done', 'CLOSE')], default='assign',
        track_visibility='onchange', readonly=True, copy=False, string="Stage")

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_sale_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_sale_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    @api.returns('self')
    def _default_stage(self):
        return self.env['stock.picking.states'].search([], limit=1)

    so_state = fields.Many2many("stock.picking.states", default=_default_stage)
    cancel_state = fields.Char("Last State")
    approved_by=fields.Char(string="Approved By",track_visibility='onchange')
    reason_approve = fields.Char(string="Reason",track_visibility='onchange')
    shipping_terms = fields.Selection([('quoted', 'Quoted'), ('prepaid', 'Prepaid'), ('collect', 'Collect'), ('free', 'Free')], default='quoted' , string='Shipping Terms')
    hold_lastval = fields.Float("Approved")
    is_portal_authorised = fields.Boolean(
        string='Is portal authorised',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    backorder = fields.Selection([('contact before shipping partial','Contact Before Shipping Partial'),
                ('ship partial, contact when restocked','Ship Partial, Contact When Restocked'),
                ('ship partial, ship when restocked','Ship Partial, Ship When Restocked'),
                ('ship partial, cancel backorder', 'Ship Partial, Cancel Backorder'),('cancel','Cancel')], 
                string="Backorders")
    customer_priority = fields.Selection([('ready', "I’m ready to order"),
        ('plan', "I plan to order soon"),
        ('estimate', "I need an estimate for a future project")], string="Customer Priority",)

    @api.multi
    def _set_category_id(self):
        for order in self:
            computed_hide_button = self.env.user in order.review_category_id.user_ids
            if order.hide_button != computed_hide_button:
                order.hide_button = computed_hide_button

    signature = fields.Selection([('no', 'No'),('yes', 'Yes')], string='Signature', default='no')
    back_orders = fields.Char('Backorders')
    quote_template = fields.Char('Template')
    quote_draft_warning = fields.Text('Draft Warning')
    quote_warning = fields.Text('Quotation Warning')
    quote_comment = fields.Text('Comment')
    sale_assign_warn = fields.Text('Assign Warning')
    sale_release_warn = fields.Text('Release Warning')
    sale_invoice_warn = fields.Text('Invoice Warning')
    # Link buttons on sale order
    shipment_count = fields.Integer(string='Shipments', compute='_compute_shipment_ids')
    so_returns = fields.Integer('Return')
    so_packages = fields.Integer('Packages')
    so_bol = fields.Integer('BOL')
    so_invoices = fields.Integer('Invoices')
    so_credit = fields.Integer('Credits')
    so_refund = fields.Integer('Refund')
    so_support = fields.Integer('Support')
    so_authorized = fields.Float('Accepted', track_visibility='onchange')
    so_pricelist = fields.Char('Price List')

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.write({'order_stage': 'sale'})
        return res

    @api.multi
    def action_cancel(self):
        for record in self:
            if record.state == 'draft':
                record.write({'cart_state': 'cancel'})
            elif record.state == 'sent':
                record.write({'quote_stage': 'cancel'})
            elif record.state == 'order':
                record.write({'order_stage': 'cancel'})
            record.mail_sent = False
        res = super(SaleOrder, self).action_cancel()
        return res



    @api.depends('picking_ids')
    def _compute_shipment_ids(self):
        for order in self:
            order.shipment_count = len(order.picking_ids)

    @api.multi
    def view_so_shipments(self):
        '''
        This function returns an action that display existing shipments
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('shipment.custom_picking_view').read()[0]
        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('shipment.delivery_order_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        return action
    
    @api.multi
    def action_view_tasks(self):
        return True

    @api.multi
    def action_view_projects(self):
        return True

    @api.multi
    def view_so_returns(self):
        return True

    @api.multi
    def view_so_packages(self):
        return True

    @api.multi
    def view_so_bol(self):
        return True

    @api.multi
    def view_so_invoices(self):
        return True
        
    @api.multi
    def view_so_credit(self):
        return True

    @api.multi
    def view_so_support(self):
        return True
    
    ############### Lock SO ############

    lock = fields.Boolean(readonly=True, copy=False, help="if locked, you can not able to add an Item")
    
    @api.multi
    def locks(self):
        self.write({'lock': True})
    
    @api.multi
    def unlocks(self):
        self.write({'lock':False})

    @api.multi
    def action_draft(self):
        result = super(SaleOrder, self).action_draft()
        for record in self:
            if record.cart_state == 'cancel':
                record.write({'state': 'draft', 'cart_state': 'rfq'})
            elif record.quote_stage == 'cancel':
                record.write({'state': 'sent', 'quote_stage': 'draft'})
            elif record.order_stage == 'cancel':
                record.write({'state': 'order', 'order_stage': 'schedule'})
        return result

    @api.multi
    def print_quotation(self):
        self.ensure_one()
        res = super(SaleOrder, self).print_quotation()
        #if self.hold_lastval >= self.amount_total:
        #    self.write({'quote_stage':'schedule', 'lock':True})
        #else:
        self.write({'lock':True, 'quote_stage':'accept'})
        return res

    approval_threshold = fields.Float(string="Approval Threshold", track_visibility='onchange')

    @api.onchange('approval_threshold')
    def onchange_approval_threshold(self): 
        if self.approval_threshold != 0.0:
            self.need_approval = True
            #raise UserError(_('The new total must be approved by the customer or a salesperson'))

    def customer_approval(self):
        self.ensure_one()
        ship_amount = 0.0
        product_amount = 0.0
        if self.approval_required not in['no']:
            if self.approval_required in ['shipping','shipping_products']:
                ship_orderline = self.order_line.filtered(lambda line: line.product_uom_qty != line.qty_invoiced and line.is_delivery)
                ship_amount = ship_orderline.price_subtotal
            if self.approval_required in ['products','shipping_products']:
                products_orderline = self.order_line.filtered(lambda line: line.product_uom_qty != line.qty_invoiced and not line.is_delivery)
                product_amount = self.get_product_amt_withtaxes(products_orderline)

            checkamount = product_amount + ship_amount
            if checkamount > self.approval_threshold:
                if not self.approved_by  or  self.approved_by and (len(self.approved_by) < 3):
                    raise UserError(_('Approved By should be at least 3 characters'))

    ##### Approval Flow ############

    @api.multi
    def action_ready(self):
        self.write({
            'quote_stage': 'review',
        })

    @api.multi
    def action_revise(self):
        self.ensure_one()
        if self.hide_button:
            self.write({
                'quote_stage': 'revise',
            })
        else:
            raise UserError(_('Reviewer does not have access to selected Division'))

    @api.multi
    def action_accept(self):
        self.ensure_one()
        if self.env.user.id not in self.review_category_id.user_ids.ids:
            raise UserError(_('Only members of the Product Team can approve a quotation.'))
        #if self.amount_total >= self.hold_lastval:
        if True:
            self.write({'quote_stage': 'send','lock':True})

    # Stock-Reservation-Code
    reserve_count = fields.Integer(string='Reserved Orders',compute='get_total_stock_pick')
    update_reserve_stock = fields.Boolean(string="Update Reserve")
    issue_reserve_stock = fields.Boolean(string="Issue Reserve")


    def get_total_stock_pick(self):
        move_ids = self.env['stock.move'].search([('res_stock_so_id','in',self.order_line.ids)])
        res_ids = []
        for move in move_ids:
            res_ids.append(move.picking_id.id)
        self.reserve_count = len(set(res_ids))

    @api.onchange('order_line')
    def get_product_update(self):
        if self._origin:
            old_lines = []
            new_lines = []  
            for line in self.order_line:
                if type(line.id) is not int:
                    new_lines.append(line)
            if self._origin.order_line:
                for line in self._origin.order_line:
                    old_lines.append(line)
            if new_lines:
                self.issue_reserve_stock = True
            if old_lines:
                self.update_reserve_stock = True


    @api.multi
    def action_view_reserved(self):
        '''
        This function returns an action that display existing reserved orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        move_ids = self.env['stock.move'].search([('res_stock_so_id','in',self.order_line.ids)])
        res_ids = []
        for move in move_ids:
            res_ids.append(move.picking_id.id)
        #pickings = self.mapped('picking_ids')
        if len(res_ids) > 1:
            action['domain'] = [('id', 'in', res_ids)]
            action['context'] = {'create':False,'edit':False}
        elif res_ids:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
                action['context'] = {'create':False,'edit':False}
            else:
                action['views'] = form_view
                action['context'] = {'create':False,'edit':False}
            action['res_id'] = res_ids[0]
            action['context'] = {'create':False,'edit':False}
        return action

    def get_product_available_location(self, product_id, qty):
        quants = self.env['stock.quant'].search([('product_id','=',product_id.id)])
        locations = {}
        for quant in quants:
            if quant.location_id.usage == 'internal':
                locations[quant.location_id.id] = quant.quantity
            if quant.quantity >= qty:
                locations = {quant.location_id.id:quant.quantity}
                return locations
        return locations
    

    def update_reserve(self):
        fields_list = ['move_dest_exists', 'product_return_moves', 'parent_location_id', 'original_location_id', 'location_id']
        stock_move_id = None
        for line in self.order_line:
            if stock_move_id == None:
                stock_move_id = self.env['stock.move'].search([('res_stock_so_id.id','=',line.id)],limit=1)
            else:
                break
        stock_pick_ref = stock_move_id.reference
        stock_pick = self.env['stock.picking'].search([('name','=',stock_pick_ref)])
        self = self.with_context(active_id=stock_pick.id)
        pick_return_wiz = self.env['stock.return.picking'].create({'picking_id':stock_pick.id})
        wiz_default_get = pick_return_wiz.default_get(fields_list)
        for line in self.order_line:
            if line.differ_qty > 0 and (line.product_uom_qty < line.reserved_qty):
                for return_moves in pick_return_wiz.product_return_moves:
                    if return_moves.product_id.full_name == line.name:
                        return_moves.quantity = line.differ_qty
                        break
                line.differ_qty = 0

            else:
                for return_moves in pick_return_wiz.product_return_moves:
                    if (line.name == return_moves.product_id.full_name) and (line.differ_qty == 0):
                        return_moves.unlink()
                        break
                        
        wiz_return = pick_return_wiz.create_returns()
        new_pick_id = self.env['stock.picking'].search([('id','=',wiz_return['res_id'])])
        return_res = new_pick_id.button_validate()
        wiz = self.env['stock.immediate.transfer'].search([('id', '=',return_res['res_id'])])
        wiz.process()
        self.update_reserve_stock = False
        return True

    def issue_reserve(self):
        pick_id = None
        reserve_loc = self.env['stock.location'].search([('is_loc_reservable','=',True)])
        if self.stock_reserved:
            for line in self.order_line:
                if (line.differ_qty > 0) and (line.product_uom_qty > line.reserved_qty):
                    locations = self.get_product_available_location(line.product_id, line.differ_qty)
                    to_reserve = line.differ_qty
                    temp_loc = locations
                    for loc in locations:
                        if line.differ_qty <= temp_loc[loc]:
                             picking_type_id = self.env['stock.picking.type'].search([('name','=','Reserve Stock Transfers')])
                             move_id = self.env['stock.move'].create({
                                   'location_id':loc,
                                   'location_dest_id':reserve_loc.id,
                                   'product_uom_qty':line.differ_qty,
                                   'product_id': line.product_id.id,
                                   'product_uom': line.product_uom.id,
                                   'name': u"%s (%s)" % (line.order_id.name, line.name),
                                   'sale_line_id': line.id,
                                   'res_stock_so_id' : line.id,
                                   'picking_type_id' : picking_type_id.id,
                                           })
                             reserve = move_id._assign_picking()
                             pick_id = move_id.picking_id
                             break
                    line.differ_qty = 0
                elif (line.differ_qty == 0) and (line.reserved_qty == 0):
                    locations = self.get_product_available_location(line.product_id, line.product_uom_qty)
                    to_reserve = line.product_uom_qty
                    temp_loc = locations
                    for loc in locations:
                        if line.product_uom_qty <= temp_loc[loc]:
                             picking_type_id = self.env['stock.picking.type'].search([('name','=','Reserve Stock Transfers')])
                             move_id = self.env['stock.move'].create({
                                   'location_id':loc,
                                   'location_dest_id':reserve_loc.id,
                                   'product_uom_qty':line.product_uom_qty,
                                   'product_id': line.product_id.id,
                                   'product_uom': line.product_uom.id,
                                   'name': u"%s (%s)" % (line.order_id.name, line.name),
                                   'sale_line_id': line.id,
                                   'res_stock_so_id' : line.id,
                                   'picking_type_id' : picking_type_id.id,
                                           })
                             reserve = move_id._assign_picking()
                             pick_id = move_id.picking_id
                             break
            pick_confirm = pick_id.action_confirm()
            pick_assign = pick_id.action_assign()
            pick_res = pick_id.button_validate()
            wiz = self.env['stock.immediate.transfer'].search([('id', '=',pick_res['res_id'])])
            wiz.process()
        self.issue_reserve_stock = False
        return True

    def name_get(self):
        so_list = []
        for rec in self:
            if rec.partner_id:
                name = rec.name
                partner = rec.partner_id.name
                so_list.append((rec.id, "{} {}".format(name, partner)))
        return so_list

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    reserved_qty = fields.Float(string="Reserved Qty",compute="_get_reserved_qty",store=False)
    differ_qty = fields.Float(string="Differ Qty")
    order_required = fields.Integer(string="Required Order",compute="_get_product_uom_qty")
    waiting_order = fields.Integer(string="Waiting Order")
    shipped_order = fields.Integer(string="Shipped")
    invoiced_order = fields.Integer(string="Invoiced Order")

    @api.multi
    def _get_product_uom_qty(self):
        for record in self:
            if record.product_uom_qty:
                record.order_required = record.product_uom_qty

    @api.multi
    def _get_reserved_qty(self):
        for line in self:
            stock_moves_ids = line.env['stock.move'].search([])
            for move in stock_moves_ids:
                if (line.name == move.product_id.full_name) and (move.res_stock_so_id.id == line.id) and (move.location_dest_id.name == 'Reserve Stock'):
                    line.reserved_qty += move.product_uom_qty
                elif (line.name == move.product_id.full_name) and (move.res_stock_so_id.id == line.id) and (move.location_dest_id.name == 'Stock'):
                    line.reserved_qty -= move.product_uom_qty

    # @api.multi
    # def _get_reserved_qty(self):
    #     for line in self:
    #         stock_moves_ids = line.env['stock.move'].search([('res_stock_so_id.id','=',line.id),('product_id.full_name','=',line.name)])
    #         for move in stock_moves_ids:
    #             line.reserved_qty += move.product_uom_qty

    @api.onchange('product_uom_qty')
    @api.multi
    def _get_differ_qty(self):
        so_id = self.env['sale.order'].search([('name','=',self._origin.order_id.name)])
        val = {}
        for line in self:
            if line.product_uom_qty > line.reserved_qty and line.reserved_qty >= 1:
                line.differ_qty = line.product_uom_qty - line.reserved_qty
                val['issue_reserve_stock'] = True
                so_id.write(val)
            elif line.product_uom_qty < line.reserved_qty:
                line.differ_qty = line.reserved_qty - line.product_uom_qty
                val['update_reserve_stock'] = True
                so_id.write(val)

# ...............ADDING DOCUMENT PREFIX.......................

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    document_id_prefix = fields.Char(string="Sales Quotation Sequence Prefix", default=False)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        seq = self.env['ir.sequence'].search([('code','=','sale.order')])
        if seq:
            self.env['ir.config_parameter'].set_param('seq.prefix', self.document_id_prefix)
            return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        seq = self.env['ir.sequence'].search([('code', '=', 'sale.order')])
        if seq:
            doc_prefix = ICPSudo.get_param('seq.prefix')
            if doc_prefix:
                seq.prefix = doc_prefix
                res.update(
                    document_id_prefix=doc_prefix
                )
        return res
            # else:
            #     seq.prefix = 'SQ'
            #     res.update(
            #         document_id_prefix='SQ'
            #     )
            #     return res
