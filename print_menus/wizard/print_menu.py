# -*- coding: utf-8 -*- 
# Part of Odoo. See LICENSE file for full copyright and licensing details. 
from odoo import api, fields, models, _

class PrintMenu(models.TransientModel):
    _name = 'print.menu'
    _description = 'Print Menu'

    report_template = fields.Many2one('ir.actions.report', string='Print Template')
    object_name = fields.Char(string="Model Name")
    record_id = fields.Char(string="Active Id") 
    printers_ids = fields.One2many("printer.list", "printer_id", string="Printer List")

    @api.multi
    def download_report(self):
        RecordId = self.env[self.object_name].search([('id','=',self.record_id)], limit=1)
        report_template_id = self.env['ir.actions.report'].sudo().search([('id','=',self.report_template.id)], limit=1)
        report_action = report_template_id.report_action(RecordId)
        report_action['close_on_report_download']=True
        return report_action

      
class PrinterList(models.TransientModel):
    _name = 'printer.list'
    _description = 'Printer List'

    printer_id = fields.Many2one("print.menu", string="Printer Id")
  



