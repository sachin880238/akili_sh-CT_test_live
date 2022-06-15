# -*- coding: utf-8 -*-
import io
import requests
from lxml import etree, objectify
from xml.etree import ElementTree as ET
from uuid import uuid4
import pprint
import logging

from odoo.addons.payment.models.payment_acquirer import _partner_split_name
from odoo.exceptions import ValidationError, UserError
from odoo import _
from odoo.addons.payment_authorize.models import authorize_request

_logger = logging.getLogger(__name__)

XMLNS = 'AnetApi/xml/v1/schema/AnetApiSchema.xsd'


def strip_ns(xml, ns):
    """Strip the provided name from tag names.

    :param str xml: xml document
    :param str ns: namespace to strip

    :rtype: etree._Element
    :return: the parsed xml string with the namespace prefix removed
    """
    it = ET.iterparse(io.BytesIO(xml))
    ns_prefix = '{%s}' % XMLNS
    for _, el in it:
        if el.tag.startswith(ns_prefix):
            el.tag = el.tag[len(ns_prefix):]  # strip all Auth.net namespaces
    return it.root


def error_check(elem):
    """Check if the response sent by Authorize.net contains an error.

    Errors can be a failure to try the transaction (in that case, the transasctionResponse
    is empty, and the meaningful error message will be in message/code) or a failure to process
    the transaction (in that case, the message/code content will be generic and the actual error
    message is in transactionResponse/errors/error/errorText).

    :param etree._Element elem: the root element of the response that will be parsed

    :rtype: tuple (bool, str)
    :return: tuple containnig a boolean indicating if the response should be considered
             as an error and the most meaningful error message found in it.
    """
    result_code = elem.find('messages/resultCode')
    msg = 'No meaningful error message found, please check logs or the Authorize.net backend'
    has_error = result_code is not None and result_code.text == 'Error'
    if has_error:
        # accumulate the most meangingful error
        error = elem.find('transactionResponse/errors/error')
        error = error if error is not None else elem.find('messages/message')
        if error is not None:
            code = error[0].text
            text = error[1].text
            msg = '%s: %s' % (code, text)
    return (has_error, msg)


class AuthorizeAPICustom(authorize_request.AuthorizeAPI):
    """Authorize.net Gateway API integration.

    This class allows contacting the Authorize.net API with simple operation
    requests. It implements a *very limited* subset of the complete API
    (http://developer.authorize.net/api/reference); namely:
        - Customer Profile/Payment Profile creation
        - Transaction authorization/capture/voiding
    """
    # create customer payment profile for existing profile customer
    def create_customer_payment_pforile_website(self,partner, customer_profile_id, cardnumber, expiration_date, card_code):
        root = self._base_tree('createCustomerPaymentProfileRequest')
        etree.SubElement(root, "customerProfileId").text = customer_profile_id
        payment_profile = etree.SubElement(root, "paymentProfile")
        billTo = etree.SubElement(payment_profile, "billTo")
        if partner.is_company:
            etree.SubElement(billTo, "firstName").text = ' '
            etree.SubElement(billTo, "lastName").text = partner.name
        else:
            etree.SubElement(billTo, "firstName").text = _partner_split_name(partner.name)[0]
            etree.SubElement(billTo, "lastName").text = _partner_split_name(partner.name)[1]
        etree.SubElement(billTo, "address").text = (partner.street or '' + (partner.street2 if partner.street2 else '')) or None
        
        missing_fields = [partner._fields[field].string for field in ['city', 'country_id'] if not partner[field]]
        if missing_fields:
            raise ValidationError({'missing_fields': missing_fields})
        
        etree.SubElement(billTo, "city").text = partner.city
        etree.SubElement(billTo, "state").text = partner.state_id.name or None
        etree.SubElement(billTo, "zip").text = partner.zip or ''
        etree.SubElement(billTo, "country").text = partner.country_id.name or None
        payment = etree.SubElement(payment_profile, "payment")
        creditCard = etree.SubElement(payment, "creditCard")
        etree.SubElement(creditCard, "cardNumber").text = cardnumber
        etree.SubElement(creditCard, "expirationDate").text = expiration_date
        etree.SubElement(creditCard, "cardCode").text = card_code
        etree.SubElement(root, "validationMode").text = 'liveMode'
        response = self._authorize_request(root)

        msg = response.find('messages')
        if msg is not None:
            rc = msg.find('resultCode')
            if rc is not None and rc.text == 'Error':
                err = msg.find('message')
                err_code = err.find('code').text
                err_msg = err.find('text').text
                return {'err_msg':"Authorize.net Error:\nCode: %s\nMessage: %s" % (err_code, err_msg)}
        res = dict()
        res['profile_id'] = response.find('customerProfileId').text
        res['payment_profile_id'] = response.find('customerPaymentProfileIdList/numericString').text
        return res



    # Customer profiles
    def create_customer_profile_website(self, partner, cardnumber, expiration_date, card_code):
        """Create a payment and customer profile in the Authorize.net backend.

        Creates a customer profile for the partner/credit card combination and links
        a corresponding payment profile to it. Note that a single partner in the Odoo
        database can have multiple customer profiles in Authorize.net (i.e. a customer
        profile is created for every res.partner/payment.token couple).

        :param record partner: the res.partner record of the customer
        :param str cardnumber: cardnumber in string format (numbers only, no separator)
        :param str expiration_date: expiration date in 'YYYY-MM' string format
        :param str card_code: three- or four-digit verification number

        :return: a dict containing the profile_id and payment_profile_id of the
                 newly created customer profile and payment profile
        :rtype: dict
        """
        root = self._base_tree('createCustomerProfileRequest')
        profile = etree.SubElement(root, "profile")
        etree.SubElement(profile, "merchantCustomerId").text = 'ODOO-%s-%s' % (partner.id, uuid4().hex[:8])
        etree.SubElement(profile, "email").text = partner.email or ''
        payment_profile = etree.SubElement(profile, "paymentProfiles")
        etree.SubElement(payment_profile, "customerType").text = 'business' if partner.is_company else 'individual'
        billTo = etree.SubElement(payment_profile, "billTo")
        if partner.is_company:
            etree.SubElement(billTo, "firstName").text = ' '
            etree.SubElement(billTo, "lastName").text = partner.name
        else:
            etree.SubElement(billTo, "firstName").text = _partner_split_name(partner.name)[0]
            etree.SubElement(billTo, "lastName").text = _partner_split_name(partner.name)[1]
        etree.SubElement(billTo, "address").text = (partner.street or '' + (partner.street2 if partner.street2 else '')) or None
        
        missing_fields = [partner._fields[field].string for field in ['city', 'country_id'] if not partner[field]]
        if missing_fields:
            raise ValidationError({'missing_fields': missing_fields})
        
        etree.SubElement(billTo, "city").text = partner.city
        etree.SubElement(billTo, "state").text = partner.state_id.name or None
        etree.SubElement(billTo, "zip").text = partner.zip or ''
        etree.SubElement(billTo, "country").text = partner.country_id.name or None
        payment = etree.SubElement(payment_profile, "payment")
        creditCard = etree.SubElement(payment, "creditCard")
        etree.SubElement(creditCard, "cardNumber").text = cardnumber
        etree.SubElement(creditCard, "expirationDate").text = expiration_date
        etree.SubElement(creditCard, "cardCode").text = card_code
        etree.SubElement(root, "validationMode").text = 'liveMode'
        response = self._authorize_request(root)

        # If the user didn't set up authorize.net properly then the response
        # won't contain stuff like customerProfileId and accessing text
        # will raise a NoneType has no text attribute
        msg = response.find('messages')
        if msg is not None:
            rc = msg.find('resultCode')
            if rc is not None and rc.text == 'Error':
                err = msg.find('message')
                err_code = err.find('code').text
                err_msg = err.find('text').text
                return {'err_msg':"Authorize.net Error:\nCode: %s\nMessage: %s" % (err_code, err_msg)}
        res = dict()
        res['profile_id'] = response.find('customerProfileId').text
        res['payment_profile_id'] = response.find('customerPaymentProfileIdList/numericString').text
        return res
    
   