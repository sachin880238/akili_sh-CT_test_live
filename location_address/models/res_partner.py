from odoo import models, fields, api
 
class ResPartner(models.Model):
    # _name = 'res.partner'
    _inherit = 'res.partner'
    
    
    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        location_id = self.env['stock.location']
        values = {}
        if vals.get('name'):
            values['name'] = vals['name']
        else:
            values['name'] = vals['comp_name']
        values['partner_id'] = res.id
        values['code'] = res.icon_letters 
        customer_location_id =  location_id.search([('name','=','Customers')], limit=1)
        vendor_location_id =  location_id.search([('name','=','Vendors')], limit=1)
        if res.customer and not res.parent_id:
            values['usage'] = 'customer'
            if customer_location_id:
                values['location_id'] = customer_location_id.id 
                location_id.create(values)
        elif res.parent_id:
            if res.parent_id.customer:
                values['usage'] = 'customer'
                if res.type_extend == 'delivery':
                    parent_customer = location_id.search([('name','=',res.parent_id.name)], limit=1)
                    values['location_id'] = parent_customer.id
                    location_id.create(values)
        if res.supplier and not res.parent_id:
            values['usage'] = 'supplier'
            if vendor_location_id:
                values['location_id'] = vendor_location_id.id 
                location_id.create(values)
        elif res.parent_id:
            if res.parent_id.supplier:
                values['usage'] = 'supplier'
                if res.vendor_addr_type == 'delivery':
                    parent_supplier = location_id.search([('name','=',res.parent_id.name)], limit=1)
                    values['location_id'] = parent_supplier.id
                    location_id.create(values)
        return res
