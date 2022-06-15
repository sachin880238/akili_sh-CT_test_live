# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
import base64


class Binary(http.Controller):

    @http.route('/download-report/<int:report_id>', type='http', auth="public")
    @serialize_exception
    def download_document(self, report_id, **kw):
        attachment_id = http.request.env['ir.attachment'].sudo().browse(report_id)
        report_binary_data = attachment_id.datas
        filename = attachment_id.datas_fname
        filecontent = base64.b64decode(report_binary_data)
        if not filecontent:
            return request.not_found()
        else:
            return request.make_response(filecontent,
                                         [('Content-Type', 'application/octet-stream'),
                                          ('Content-Disposition', content_disposition('%s' % (attachment_id.datas_fname)))])

    @http.route(['/shop/snippet/wizard'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def snippet_wizard(self, product_id):
        product_id = request.env['product.product'].sudo().search([('id','=',product_id)])

        return request.env['ir.ui.view'].render_template("product_variant_snippets.product_variant_design",{
        'product_id':product_id,
        })
