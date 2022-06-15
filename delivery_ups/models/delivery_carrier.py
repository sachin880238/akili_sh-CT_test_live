from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import pdf

#from .ups_request import UPSRequest, Package


class ProviderUPS(models.Model):
    _inherit = 'delivery.carrier'

    def _get_ups_service_types(self):
        return [
            ('03', 'UPS Ground'),
            ('11', 'UPS Standard'),
            ('01', 'UPS Next Day'),
            ('14', 'UPS Next Day AM'),
            ('13', 'UPS Next Day Air Saver'),
            ('02', 'UPS 2nd Day'),
            ('59', 'UPS 2nd Day AM'),
            ('12', 'UPS 3-day Select'),
            ('65', 'UPS Saver'),
            ('07', 'UPS Worldwide Express'),
            ('08', 'UPS Worldwide Expedited'),
            ('54', 'UPS Worldwide Express Plus'),
            ('96', 'UPS Worldwide Express Freight')
        ]

    delivery_type = fields.Selection(selection_add=[('ups', "UPS")])
    ups_bill_my_account = fields.Boolean(string='Bill My Account', help="If checked, ecommerce users will be prompted their UPS account number\n"
                                                                        "and delivery fees will be charged on it.")
    ups_cod = fields.Boolean(string='Collect on Delivery',
        help='This value added service enables UPS to collect the payment of the shipment from your customer.')
    ups_saturday_delivery = fields.Boolean(string='UPS Saturday Delivery',
        help='This value added service will allow you to ship the package on saturday also.')
    ups_cod_funds_code = fields.Selection(selection=[
        ('0', "Check, Cashier's Check or MoneyOrder"),
        ('8', "Cashier's Check or MoneyOrder"),
        ], string='COD Funding Option', default='0')
    ups_user = fields.Char(string='UPS User', groups="base.group_system")
    ups_password = fields.Char(string='UPS Password', groups="base.group_system")
    ups_shipper_nbr = fields.Char(string='UPS Shipper No.')
    ups_access_nbr = fields.Char(string='UPS AccessLicense No')
    ups_default_packaging_id = fields.Many2one('product.packaging', string='UPS Default Packaging Type')
    ups_default_service_type = fields.Selection(_get_ups_service_types,string="UPS Service Type", default='03')
    ups_package_wgt_unit = fields.Selection([('LBS', 'Pounds'), ('KGS', 'Kilograms')], default='KGS')
    ups_package_dimension_unit = fields.Selection([('IN', 'Inches'), ('CM', 'Centimeters')], string="Units for UPS Package Size", default='IN')
    ups_label_file_type = fields.Selection([('GIF', 'PDF'),
                                            ('ZPL', 'ZPL'),
                                            ('EPL', 'EPL'),
                                            ('SPL', 'SPL')],
                                           string="UPS Label File Type", default='GIF')

    @api.onchange('ups_default_service_type')
    def on_change_service_type(self):
        self.ups_cod = False
        self.ups_saturday_delivery = False

    def ups_rate_shipment(self, order):
        superself = self.sudo()
        srm = UPSRequest(self.log_xml, superself.ups_user, superself.ups_password, superself.ups_shipper_nbr, superself.ups_access_nbr, self.prod_environment)
        ResCurrency = self.env['res.currency']
        max_weight = self.ups_default_packaging_id.max_weight
        packages = []
        total_qty = 0
        total_weight = 0
        for line in order.order_line.filtered(lambda line: not line.is_delivery):
            total_qty += line.product_uom_qty
            total_weight += line.product_id.weight * line.product_qty

        if max_weight and total_weight > max_weight:
            total_package = int(total_weight / max_weight)
            last_package_weight = total_weight % max_weight

            for seq in range(total_package):
                packages.append(Package(self, max_weight))
            if last_package_weight:
                packages.append(Package(self, last_package_weight))
        else:
            packages.append(Package(self, total_weight))

        shipment_info = {
            'total_qty': total_qty  # required when service type = 'UPS Worldwide Express Freight'
        }

        if self.ups_cod:
            cod_info = {
                'currency': order.partner_id.country_id.currency_id.name,
                'monetary_value': order.amount_total,
                'funds_code': self.ups_cod_funds_code,
            }
        else:
            cod_info = None

        check_value = srm.check_required_value(order.company_id.partner_id, order.warehouse_id.partner_id, order.partner_shipping_id, order=order)
        if check_value:
            return {'success': False,
                    'price': 0.0,
                    'error_message': check_value,
                    'warning_message': False}

        ups_service_type = order.ups_service_type or self.ups_default_service_type
        result = srm.get_shipping_price(
            shipment_info=shipment_info, packages=packages, shipper=order.company_id.partner_id, ship_from=order.warehouse_id.partner_id,
            ship_to=order.partner_shipping_id, packaging_type=self.ups_default_packaging_id.shipper_package_code, service_type=ups_service_type,
            saturday_delivery=self.ups_saturday_delivery, cod_info=cod_info)

        if result.get('error_message'):
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error:\n%s') % result['error_message'],
                    'warning_message': False}

        if order.currency_id.name == result['currency_code']:
            price = float(result['price'])
        else:
            quote_currency = ResCurrency.search([('name', '=', result['currency_code'])], limit=1)
            price = quote_currency._convert(
                float(result['price']), order.currency_id, order.company_id, order.date_order or fields.Date.today())

        if self.ups_bill_my_account and order.ups_carrier_account:
            # Don't show delivery amount, if ups bill my account option is true
            price = 0.0

        return {'success': True,
                'price': price,
                'error_message': False,
                'warning_message': False}

    def ups_send_shipping(self, pickings):
        res = []
        superself = self.sudo()
        srm = UPSRequest(self.log_xml, superself.ups_user, superself.ups_password, superself.ups_shipper_nbr, superself.ups_access_nbr, self.prod_environment)
        ResCurrency = self.env['res.currency']
        for picking in pickings:
            packages = []
            package_names = []
            if picking.package_ids:
                # Create all packages
                for package in picking.package_ids:
                    packages.append(Package(self, package.shipping_weight, quant_pack=package.packaging_id, name=package.name))
                    package_names.append(package.name)
            # Create one package with the rest (the content that is not in a package)
            if picking.weight_bulk:
                packages.append(Package(self, picking.weight_bulk))

            invoice_line_total = 0
            for move in picking.move_lines:
                invoice_line_total += picking.company_id.currency_id.round(move.product_id.lst_price * move.product_qty)

            shipment_info = {
                'description': picking.origin,
                'total_qty': sum(sml.qty_done for sml in picking.move_line_ids),
                'ilt_monetary_value': '%d' % invoice_line_total,
                'itl_currency_code': self.env.user.company_id.currency_id.name,
                'phone': picking.partner_id.mobile or picking.partner_id.phone or picking.sale_id.partner_id.mobile or picking.sale_id.partner_id.phone,
            }
            ups_service_type = picking.ups_service_type or self.ups_default_service_type
            ups_carrier_account = picking.ups_carrier_account

            if picking.carrier_id.ups_cod:
                cod_info = {
                    'currency': picking.partner_id.country_id.currency_id.name,
                    'monetary_value': picking.sale_id.amount_total,
                    'funds_code': self.ups_cod_funds_code,
                }
            else:
                cod_info = None

            check_value = srm.check_required_value(picking.company_id.partner_id, picking.picking_type_id.warehouse_id.partner_id, picking.partner_id, picking=picking)
            if check_value:
                raise UserError(check_value)

            package_type = picking.package_ids and picking.package_ids[0].packaging_id.shipper_package_code or self.ups_default_packaging_id.shipper_package_code
            result = srm.send_shipping(
                shipment_info=shipment_info, packages=packages, shipper=picking.company_id.partner_id, ship_from=picking.picking_type_id.warehouse_id.partner_id,
                ship_to=picking.partner_id, packaging_type=package_type, service_type=ups_service_type, label_file_type=self.ups_label_file_type, ups_carrier_account=ups_carrier_account,
                saturday_delivery=picking.carrier_id.ups_saturday_delivery, cod_info=cod_info)
            if result.get('error_message'):
                raise UserError(result['error_message'])

            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            currency_order = picking.sale_id.currency_id
            if not currency_order:
                currency_order = picking.company_id.currency_id

            if currency_order.name == result['currency_code']:
                price = float(result['price'])
            else:
                quote_currency = ResCurrency.search([('name', '=', result['currency_code'])], limit=1)
                price = quote_currency._convert(
                    float(result['price']), currency_order, company, order.date_order or fields.Date.today())

            package_labels = []
            for track_number, label_binary_data in result.get('label_binary_data').items():
                package_labels = package_labels + [(track_number, label_binary_data)]

            carrier_tracking_ref = "+".join([pl[0] for pl in package_labels])
            logmessage = _("Shipment created into UPS<br/>"
                           "<b>Tracking Numbers:</b> %s<br/>"
                           "<b>Packages:</b> %s") % (carrier_tracking_ref, ','.join(package_names))
            if self.ups_label_file_type != 'GIF':
                attachments = [('LabelUPS-%s.%s' % (pl[0], self.ups_label_file_type), pl[1]) for pl in package_labels]
            if self.ups_label_file_type == 'GIF':
                attachments = [('LabelUPS.pdf', pdf.merge_pdf([pl[1] for pl in package_labels]))]
            picking.message_post(body=logmessage, attachments=attachments)
            shipping_data = {
                'exact_price': price,
                'tracking_number': carrier_tracking_ref}
            res = res + [shipping_data]
        return res

    def ups_get_tracking_link(self, picking):
        return 'http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=%s' % picking.carrier_tracking_ref.replace('+', '%0A')

    def ups_cancel_shipment(self, picking):
        tracking_reference = picking.carrier_tracking_ref
        if not self.prod_environment:
            tracking_reference = "1ZISDE016691676846"  # used for testing purpose

        superself = self.sudo()
        srm = UPSRequest(self.log_xml, superself.ups_user, superself.ups_password, superself.ups_shipper_nbr, superself.ups_access_nbr, self.prod_environment)
        result = srm.cancel_shipment(tracking_reference)

        if result.get('error_message'):
            raise UserError(result['error_message'])
        else:
            picking.message_post(body=_(u'Shipment N° %s has been cancelled' % picking.carrier_tracking_ref))
            picking.write({'carrier_tracking_ref': '',
                           'carrier_price': 0.0})

    def _ups_get_default_custom_package_code(self):
        return '02'

    def _ups_convert_weight(self, weight, unit='KGS'):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if unit == 'KGS':
            return weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_kgm'), round=False)
        elif unit == 'LBS':
            return weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_lb'), round=False)
        else:
            raise ValueError



class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'


    module_delivery_ups_custom = fields.Boolean("UPS Connector")


from odoo import api, models, fields, _

#from .ups_request import UPSRequest, Package


class EchoEstimatorLines(models.TransientModel):
    _name = 'echo.estimator.lines'

    
    price = fields.Float('Price')
    sale_order_line = fields.Many2one('sale.order.line')
    select = fields.Boolean(string='Select')
    carrier_id = fields.Many2one('delivery.carrier',string='Via')
    days = fields.Float(string='Days')
    cost = fields.Float('Cost')
    packangin_rate = fields.Float('Pacakaging')
    insurence = fields.Float('Insurence')
    multiplier = fields.Float('Multiplier')
    echoestimator_id = fields.Many2one('echo.estimator')


class EchoEstimator(models.TransientModel):
    _name = 'echo.estimator'

    
    echo_estimator_lines = fields.One2many('echo.estimator.lines','echoestimator_id')
    company_id = fields.Many2one('res.company',string='Origin')
    destination_type = fields.Selection([('residential', 'Residential'), ('commercial', 'Commercial')], default='residential',string="Destination Type")
    special_handling = fields.Selection([('liftgate', 'Lift Gate'), ('inside_delivery', 'Inside Delivery')],string="Special Handling")
    notification = fields.Selection([('contact_before_delivery', 'Contact Before Delivery'),('none','None')],string="Notification")
    insurence = fields.Selection([('carrier_included','Carrier Included'),('full_value','Full Value')],string="Insurence")
    length_of_trailer = fields.Float()
    length_of_container = fields.Float()
    sale_id = fields.Many2one('sale.order')
    # destination = fields.Text('Destination',related='sale_id.partner_shipping_id')
    destination = fields.Many2one('res.partner',string='Destination', related='sale_id.partner_shipping_id')




class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    
    def echo_estimated_wizard(self):
        wizard_form = self.env.ref('delivery_ups.shipping_estimator_form')
        return {
            'name' : _('Add Shipping'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'echo.estimator',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_sale_id':self.id}
        }
    