# coding: utf-8
from werkzeug import urls

from .authorize_request import AuthorizeAPICustom
from datetime import datetime
import hashlib
import hmac
import logging
import string
import time

from odoo import _, api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_authorize.controllers.main import AuthorizeController
from odoo.tools.float_utils import float_compare, float_repr
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PaymentAcquirerAuthorize(models.Model):
    _inherit = 'payment.acquirer'

    def function():
        pass


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_profile_id = fields.Char(
         string='Customer profile id',
         required=False,
         readonly=False,
         index=False,
         default=0,
         help=False
    )

    customerPaymentProfile_ids = fields.Many2many(
        string='CustomerPaymentProfile ids',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='customer.payment.profile',
        relation='res_partner_customer_payment_profile_rel',
        column1='partner_id',
        column2='customer_payment_profile_id',
        domain=[],
        context={},
        limit=None
    )

    @api.multi
    def create_add_payment_profile(self,values,customer_profile_id):
        if values.get('debit_card_no'):
            values['debit_card_no'] = values['debit_card_no'].replace(' ', '')
            acquirer = self.env['payment.acquirer'].browse(4)
            expiry = str(values['year']) + str(values['month'])
            partner = self.env['res.partner'].browse(int(values['billing_address_id']))
            transaction = AuthorizeAPICustom(acquirer)
            res = transaction.create_customer_payment_pforile_website(partner,customer_profile_id,values['debit_card_no'], expiry, values['cvv_code'])

            return res

 
    @api.multi
    def create_partner_authorize_profile(self,values):
        if values.get('debit_card_no'):
            values['debit_card_no'] = values['debit_card_no'].replace(' ', '')
            acquirer = self.env['payment.acquirer'].browse(4)
            expiry = str(values['year']) + str(values['month'])
            partner = self.env['res.partner'].browse(int(values['billing_address_id']))
            transaction = AuthorizeAPICustom(acquirer)
            res = transaction.create_customer_payment_pforile_website(partner, values['debit_card_no'], expiry, values['cvv_code'])

            return res
            # if res.get('profile_id') and res.get('payment_profile_id'):
            #     return {
            #         'authorize_profile': res.get('profile_id'),
            #         'name': 'XXXXXXXXXXXX%s - %s' % (values['cc_number'][-4:], values['cc_holder_name']),
            #         'acquirer_ref': res.get('payment_profile_id'),
            #     }
            # else:
            #     raise ValidationError(_('The Customer Profile creation in Authorize.NET failed.'))
        else:
            return values


 


   
class CustomerPaymentProfile(models.Model):
    _name = 'customer.payment.profile'
    _description = 'Customer Payment Profile'

    card_holder_name = fields.Char(
        string='Card holder name',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=True
    )

    payment_profile_id = fields.Char(
        string='Payment profile id',
        required=False,
        readonly=False,
        index=False,
        default=0,
        help=False
    )


    customer_profile_id = fields.Char(
         string='Customer profile id',
         required=False,
         readonly=False,
         index=False,
         default=0,
         help=False
    )

    


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_payment_token = fields.Integer(
        string='Customer payment token',
        required=False,
        readonly=True,
        index=False,
        default=0,
        help=False
    )


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    authorize_profile = fields.Char(string='Authorize.net Profile ID', help='This contains the unique reference '
                                    'for this partner/payment token combination in the Authorize.net backend')
    provider = fields.Selection(string='Provider', related='acquirer_id.provider', readonly=False)
    save_token = fields.Selection(string='Save Cards', related='acquirer_id.save_token', readonly=False)

    @api.model
    def authorize_create(self, values):
        if values.get('cc_number'):
            values['cc_number'] = values['cc_number'].replace(' ', '')
            acquirer = self.env['payment.acquirer'].browse(values['acquirer_id'])
            expiry = str(values['cc_expiry'][:2]) + str(values['cc_expiry'][-2:])
            partner = self.env['res.partner'].browse(values['partner_id'])
            transaction = AuthorizeAPI(acquirer)
            res = transaction.create_customer_profile(partner, values['cc_number'], expiry, values['cc_cvc'])
            if res.get('profile_id') and res.get('payment_profile_id'):
                return {
                    'authorize_profile': res.get('profile_id'),
                    'name': 'XXXXXXXXXXXX%s - %s' % (values['cc_number'][-4:], values['cc_holder_name']),
                    'acquirer_ref': res.get('payment_profile_id'),
                }
            else:
                raise ValidationError(_('The Customer Profile creation in Authorize.NET failed.'))
        else:
            return values
