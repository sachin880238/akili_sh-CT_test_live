# -*- coding: utf-8 -*-
# Copyright 2018 Akili Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def add_line_sale_order_options(self): 
        wizard_form = self.env.ref('quotation_options_line.order_line_options_form_views')
        return {
            'name' : _('Add Product'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'sale.order.option',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'order_line_type' : 'line', 'default_order_id': self.id}
        } 

    @api.multi
    def add_set_product_options(self):
        wizard_form = self.env.ref('quotation_options_line.option_set_form_views') 
        return {
            'name' : _('Add Set'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'options.set',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'order_line_type': 'set'}
        }

    # Move line for select option product line    
    @api.multi
    def move_orderlines_to_option(self):
        wizard_form = self.env.ref('quotation_options_line.move_lines_product_views')
        if not self._context.get('selected_o2m_ids'):
            raise UserError(_('Please Select at least One Line to Perform this Action!!!'))          
        return {
            'name' : _('Move to Products'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'move.lines.product',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'select_order_line': self._context.get('selected_o2m_ids')}
        }         
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            product=self.product_id.id
            partners=self.env.user.partner_id
            date=False
            uom_id=False
            quantities=1
            results = {}
            products_qty_partner=[(product, quantities, partners)]
            self.ensure_one()
            if not date:
                date = self._context.get('date') or fields.Date.today()
            date = fields.Date.to_date(date)  # boundary conditions differ if we have a datetime
            if not uom_id and self._context.get('uom'):
                uom_id = self._context['uom']
            # if uom_id:
            #     # rebrowse with uom if given
            #     products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            #     products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
            # else:
            #     products = [item[0] for item in products_qty_partner]

            # if not products:
            #     return {}

            categ_ids = {}
            for p in self.product_id:
                categ = p.categ_id
                while categ:
                    categ_ids[categ.id] = True
                    categ = categ.parent_id
            categ_ids = list(categ_ids)
            prod_ids = [product.id for product in self.product_id]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in self.product_id]
            temp=[]
            for pricelist in self.env['product.pricelist'].sudo().search([]):
                items = pricelist._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)
                results[self.product_id.id] = 0.0
                suitable_rule = False
                product=self.product_id
                qty_uom_id = self._context.get('uom') or product.uom_id.id
                price_uom_id = product.uom_id.id
                price_uom = self.env['uom.uom'].browse([qty_uom_id])
                for rule in items:
                    if self.product_uom_qty >= rule.min_quantity:
                        price = product.price_compute(rule.base)[product.id]
                        convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                        if price is not False:
                            if rule.compute_price == 'fixed':
                                price = convert_to_price_uom(rule.fixed_price)
                            elif rule.compute_price == 'percentage':
                                price = (price - (price * (rule.percent_price / 100))) or 0.0
                            else:
                                # complete formula
                                price_limit = price
                                price = (price - (price * (rule.price_discount / 100))) or 0.0
                                if rule.price_round:
                                    price = tools.float_round(price, precision_rounding=rule.price_round)

                                if rule.price_surcharge:
                                    price_surcharge = convert_to_price_uom(rule.price_surcharge)
                                    price += price_surcharge

                                if rule.price_min_margin:
                                    price_min_margin = convert_to_price_uom(rule.price_min_margin)
                                    price = max(price, price_limit + price_min_margin)

                                if rule.price_max_margin:
                                    price_max_margin = convert_to_price_uom(rule.price_max_margin)
                                    price = min(price, price_limit + price_max_margin)
                            suitable_rule = rule
                            
                            # Final price conversion into pricelist currency
                        if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                            if suitable_rule.base == 'standard_price':
                                cur = product.cost_currency_id
                            else:
                                cur = product.currency_id
                            price = cur._convert(price, self.currency_id, self.env.user.company_id, date, round=False)

                        if not suitable_rule:
                            cur = product.currency_id
                            price = cur._convert(price, self.currency_id, self.env.company, date, round=False)    
                        results[product.id] = round(price,2)
                        temp.append(results[product.id])
            self.price_unit=min(temp)
            self.price_subtotal=self.product_uom_qty*self.price_unit
        return res


    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if self.product_id:
            product=self.product_id.id
            partners=self.env.user.partner_id
            date=False
            uom_id=False
            quantities=1
            results = {}
            products_qty_partner=[(product, quantities, partners)]
            self.ensure_one()
            if not date:
                date = self._context.get('date') or fields.Date.today()
            date = fields.Date.to_date(date)  # boundary conditions differ if we have a datetime
            if not uom_id and self._context.get('uom'):
                uom_id = self._context['uom']
            # if uom_id:
            #     # rebrowse with uom if given
            #     products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            #     products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
            # else:
            #     products = [item[0] for item in products_qty_partner]

            # if not products:
            #     return {}

            categ_ids = {}
            for p in self.product_id:
                categ = p.categ_id
                while categ:
                    categ_ids[categ.id] = True
                    categ = categ.parent_id
            categ_ids = list(categ_ids)
            prod_ids = [product.id for product in self.product_id]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in self.product_id]
            temp=[]
            for pricelist in self.env['product.pricelist'].sudo().search([]):
                items = pricelist._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)
                results[self.product_id.id] = 0.0
                suitable_rule = False
                product=self.product_id
                qty_uom_id = self._context.get('uom') or product.uom_id.id
                price_uom_id = product.uom_id.id
                price_uom = self.env['uom.uom'].browse([qty_uom_id])
                for rule in items:
                    if self.product_uom_qty >= rule.min_quantity:
                        price = product.price_compute(rule.base)[product.id]
                        convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                        if price is not False:
                            if rule.compute_price == 'fixed':
                                price = convert_to_price_uom(rule.fixed_price)
                            elif rule.compute_price == 'percentage':
                                price = (price - (price * (rule.percent_price / 100))) or 0.0
                            else:
                                # complete formula
                                price_limit = price
                                price = (price - (price * (rule.price_discount / 100))) or 0.0
                                if rule.price_round:
                                    price = tools.float_round(price, precision_rounding=rule.price_round)

                                if rule.price_surcharge:
                                    price_surcharge = convert_to_price_uom(rule.price_surcharge)
                                    price += price_surcharge

                                if rule.price_min_margin:
                                    price_min_margin = convert_to_price_uom(rule.price_min_margin)
                                    price = max(price, price_limit + price_min_margin)

                                if rule.price_max_margin:
                                    price_max_margin = convert_to_price_uom(rule.price_max_margin)
                                    price = min(price, price_limit + price_max_margin)
                            suitable_rule = rule
                            
                            # Final price conversion into pricelist currency
                        if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                            if suitable_rule.base == 'standard_price':
                                cur = product.cost_currency_id
                            else:
                                cur = product.currency_id
                            price = cur._convert(price, self.currency_id, self.env.user.company_id, date, round=False)

                        if not suitable_rule:
                            cur = product.currency_id
                            price = cur._convert(price, self.currency_id, self.env.company, date, round=False)    
                        results[product.id] = round(price,2)
                        temp.append(results[product.id])
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            self.price_unit=min(temp)
            self.price_subtotal=self.product_uom_qty*self.price_unit
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                                (self.product_id.virtual_available, product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search([]):
                            quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                            if quantity > 0:
                                message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message' : message
                    }
                    return {'warning': warning_mess}
        return {}

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )


    def compute_price_for_website(self):
        if self.product_id:
            product=self.product_id.id
            partners=self.env.user.partner_id
            date=False
            uom_id=False
            quantities=1
            results = {}
            products_qty_partner=[(product, quantities, partners)]
            self.ensure_one()
            if not date:
                date = self._context.get('date') or fields.Date.today()
            date = fields.Date.to_date(date)  # boundary conditions differ if we have a datetime
            if not uom_id and self._context.get('uom'):
                uom_id = self._context['uom']
            # if uom_id:
            #     # rebrowse with uom if given
            #     products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            #     products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
            # else:
            #     products = [item[0] for item in products_qty_partner]

            # if not products:
            #     return {}

            categ_ids = {}
            for p in self.product_id:
                categ = p.categ_id
                while categ:
                    categ_ids[categ.id] = True
                    categ = categ.parent_id
            categ_ids = list(categ_ids)
            prod_ids = [product.id for product in self.product_id]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in self.product_id]
            temp=[]
            for pricelist in self.env.user.partner_id.property_product_pricelist:
                items = pricelist._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)
                results[self.product_id.id] = 0.0
                suitable_rule = False
                product=self.product_id
                qty_uom_id = self._context.get('uom') or product.uom_id.id
                price_uom_id = product.uom_id.id
                price_uom = self.env['uom.uom'].browse([qty_uom_id])
                for rule in items:
                    if self.product_uom_qty >= rule.min_quantity:
                        price = product.price_compute(rule.base)[product.id]
                        convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                        if price is not False:
                            if rule.compute_price == 'fixed':
                                price = convert_to_price_uom(rule.fixed_price)
                            elif rule.compute_price == 'percentage':
                                price = (price - (price * (rule.percent_price / 100))) or 0.0
                            else:
                                # complete formula
                                price_limit = price
                                price = (price - (price * (rule.price_discount / 100))) or 0.0
                                if rule.price_round:
                                    price = tools.float_round(price, precision_rounding=rule.price_round)

                                if rule.price_surcharge:
                                    price_surcharge = convert_to_price_uom(rule.price_surcharge)
                                    price += price_surcharge

                                if rule.price_min_margin:
                                    price_min_margin = convert_to_price_uom(rule.price_min_margin)
                                    price = max(price, price_limit + price_min_margin)

                                if rule.price_max_margin:
                                    price_max_margin = convert_to_price_uom(rule.price_max_margin)
                                    price = min(price, price_limit + price_max_margin)
                            suitable_rule = rule
                            
                            # Final price conversion into pricelist currency
                        if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                            if suitable_rule.base == 'standard_price':
                                cur = product.cost_currency_id
                            else:
                                cur = product.currency_id
                            price = cur._convert(price, self.currency_id, self.env.user.company_id, date, round=False)

                        if not suitable_rule:
                            cur = product.currency_id
                            price = cur._convert(price, self.currency_id, self.env.company, date, round=False)    
                        results[product.id] = round(price,2)
                        temp.append(results[product.id])
            self.price_unit=min(temp)
            self.price_subtotal=self.product_uom_qty*self.price_unit

            #self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)



class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'





    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        self.ensure_one()
        # Load all rules
        #self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id'])
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                product_pricelist_item AS item
            LEFT JOIN product_category AS categ ON item.categ_id = categ.id
            WHERE
                (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                AND (item.product_id IS NULL OR item.product_id = any(%s))
                AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                AND (item.pricelist_id = %s)
                AND (item.date_start IS NULL OR item.date_start<=%s)
                AND (item.date_end IS NULL OR item.date_end>=%s)
            ORDER BY
                item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
            """,
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))
        # NOTE: if you change `order by` on that query, make sure it matches
        # _order from model to avoid inconstencies and undeterministic issues.

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env['product.pricelist.item'].browse(item_ids)
