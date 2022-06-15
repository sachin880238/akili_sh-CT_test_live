from odoo import fields, models, api


class Territories(models.Model):
	_name = 'territories.territories'

	name = fields.Char('Territory Name', readonly=True)
	territory_id = fields.Char('Territory ID')
	parent_id = fields.Many2one('territories.territories', 'Parent Name')
	parent_code = fields.Char('Parent Code', readonly=True)
	territory_name = fields.Char('Territory Name')
	territory_code = fields.Char('Territory Code')
	comment = fields.Text('Comment')
	state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('inactive', 'Inactive')], default="draft", string='State')


	@api.onchange('parent_id')
	def change_parent_id(self):
		if self.parent_id:
			teritory = self.parent_id.name.split(" ")
			code = ""
			for i in teritory:
				code = code + "" + i[0]
			self.parent_code = code
		else:
			self.parent_code = ""

	@api.model
	def create(self, vals):
		ter_id = vals.get('territory_id')
		par_code = vals.get('parent_code')
		terr_code = vals.get('territory_code')
		name = str(ter_id)+str(par_code)+"/"+str(terr_code)
		vals['name'] = name
		return super(Territories, self).create(vals)

	def active(self):
		self.state = 'active'

	def inactive(self):
		self.state = 'inactive'

	def reset(self):
		self.state = 'draft'
