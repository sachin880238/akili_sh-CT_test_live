from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls):
        align_id = request.env['ir.config_parameter'].search([('key','=','align')])
        if align_id:
            if align_id.value == 'True':
                request.session['align'] = True
            else:
                request.session['align'] = False
        else:
            request.session['align'] = False
        return super(IrHttp, cls)._dispatch()
