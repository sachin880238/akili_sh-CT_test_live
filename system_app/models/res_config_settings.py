# -*- coding: utf-8 -*-
from odoo import fields, models, api





class ResConfigSettings(models.TransientModel):

	_inherit = 'res.config.settings'


	sale = fields.Boolean('Sales',config_parameter='sale.sale')
	crm = fields.Boolean('CRM',config_parameter='logo.logo')
	purchase = fields.Boolean('Purchase',config_parameter='purchase.purchase')
	inventory = fields.Boolean('Inventory',config_parameter='inventory.inventory')
	mrp = fields.Boolean('Manufacturing',config_parameter='mrp.mrp')
	helpdesk = fields.Boolean('Helpdesk',config_parameter='helpdesk.helpdesk')
	




	@api.model
	def create(self,vals):
		
		search_module = self.env['ir.module.module'].search([('name', '=', 'sale_management')])
		if vals['sale'] :
			search_module.button_immediate_install()
		if not vals['sale'] : 
			search_module.button_immediate_uninstall()

		search_module = self.env['ir.module.module'].search([('name', '=', 'purchase')])
		if vals['purchase'] :
			search_module.button_immediate_install()
		if not vals['purchase'] :
			search_module.button_immediate_uninstall()

		search_module = self.env['ir.module.module'].search([('name', '=', 'stock')])
		if vals['inventory'] :
			search_module.button_immediate_install()
		if not vals['inventory'] :
			search_module.button_immediate_uninstall()		

		search_module = self.env['ir.module.module'].search([('name', '=', 'crm')])
		if vals['crm'] :
			search_module.button_immediate_install()
		if not vals['crm'] : 
			search_module.button_immediate_uninstall()

		search_module = self.env['ir.module.module'].search([('name', '=', 'mrp')])
		if vals['mrp'] :
			search_module.button_immediate_install()
		if not vals['mrp'] : 
			search_module.button_immediate_uninstall()	

		search_module = self.env['ir.module.module'].search([('name', '=', 'helpdesk')])
		if vals['helpdesk'] :
			search_module.button_immediate_install()
		if not vals['helpdesk'] : 
			search_module.button_immediate_uninstall()
				

		record = super(ResConfigSettings, self).create(vals)															
		return record

