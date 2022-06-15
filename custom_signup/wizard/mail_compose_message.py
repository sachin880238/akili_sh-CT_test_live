# -*- coding: utf-8 -*-
import datetime
import random
from urllib.parse import urljoin
import werkzeug

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MailComposer(models.TransientModel):
    
    _inherit = 'mail.compose.message'


    def send_mail_action(self):
        partner_ids = self.partner_ids
        template_id = self.env.ref('sale.email_template_edi_sale').id

        if ((self.template_id.id == template_id) and partner_ids):
            user_id = False
            
            for partner_id in partner_ids:
                user_ids = self.env['res.users'].search([])

                user_exists = False
                for user_id in user_ids:
                    if user_id.partner_id == partner_id:
                        user_exists = user_id
                        break

                if not user_exists:
                    user_id =False

            # url = self.replace_login_url_in_template(user_id)

            res = super(MailComposer, self).send_mail_action()
        else:
            res = super(MailComposer, self).send_mail_action()
        
        return res
