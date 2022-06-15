from odoo import api, fields, models


class WebsiteCategory(models.Model):

    _inherit = "product.public.category"


    state = fields.Selection([
             ('active', 'Active'),
             ('inactive', 'Inactive')],string="State",default="active")
    category_name = fields.Char('Category')
    childern_name = fields.Char('All Children')
    comment = fields.Text('Comment')
    image = fields.Binary("Image")
    
    def name_get(self):
        res = []
        for category in self:
            if category.parent_id.name or category.name:
                names = [category.name]
                parent_category = category.parent_id
                while parent_category:
                    names.append(parent_category.name)
                    parent_category = parent_category.parent_id
                res.append((category.id, '/ '.join(map(str,reversed(names)))))
            else:
                res.append((category.id, 'New'))
        return res


    def action_inactive(self):
    	self.state='inactive'


    def action_active(self):
    	self.state='active'


    @api.model
    def create(self, vals):
        res = super(WebsiteCategory, self).create(vals)

        search_record = self.env['website.menu'].search([('is_for_catag', '=', True)])
        shop_record = self.env['website.menu'].search([('name', '=', 'Shop'),('url', '=', '#')])

        if vals.get('parent_id')==False and search_record:
            values = {}
            values['name'] = vals['name']
            values['url'] = '/find-a-product-menu/%s'%(res.id)
            values['is_active'] = True
            values['image'] = vals['image']
            values['comment'] = vals['comment']
            values['sequence'] = search_record.sequence + 1
            values['website_product_catag_id'] = res.id
            result = self.env['website.menu'].create(values)
            parent_result = result
            shop_record.write({'url':'#','child_id': [(4,  result.id)]})

        elif vals.get('parent_id') and search_record:
            parent_record = self.env['website.menu'].search([('website_product_catag_id', '=', vals.get('parent_id')),('is_for_child_catag', '=', False)])
            values = {}
            values['name'] = vals['name']
            values['url'] = '/find-a-product-menu/%s'%(res.id)
            values['is_active'] = True
            values['image'] = vals['image']
            values['comment'] = vals['comment']
            # values['sequence'] = search_record.sequence + 1
            values['website_product_catag_id'] = res.id
            result = self.env['website.menu'].create(values)
            parent_result = result
            parent_record.write({'url':'#','child_id': [(4,  result.id)]})

        if vals.get('childern_name') and search_record:
            values = {}
            values['name'] = vals['childern_name']
            values['url'] = '/find-a-product-menu/%s'%(res.id)
            values['is_active'] = True
            values['image'] = vals['image']
            values['comment'] = vals['comment']
            values['is_for_child_catag'] = True
            values['sequence'] = search_record.sequence + 1
            values['website_product_catag_id'] = res.id
            result = self.env['website.menu'].create(values)
            parent_result.write({'url':'#','child_id': [(4,  result.id)]})              

        return res

    @api.multi
    def write(self, vals):
        res = super(WebsiteCategory, self).write(vals)
        search_record = self.env['website.menu'].search([('is_for_catag', '=', True)])
        write_record = self.env['website.menu'].search([('website_product_catag_id', '=', self.id)])

        if 'parent_id' not in vals.keys() and 'image' not in vals.keys() and 'comment' not in vals.keys() and 'childern_name' not in vals.keys() and 'state' not in vals.keys() and search_record:
            values = {}
            values['name'] = vals['name']
            result = write_record.write(values)

        elif 'childern_name' in vals.keys():
            write_chil_record = self.env['website.menu'].search([('website_product_catag_id', '=', self.id),('is_for_child_catag', '=', True)])
            values = {}
            values['name'] = vals['childern_name']
            result = write_chil_record.write(values)

        elif 'parent_id' in vals.keys() and search_record:
            parent_record = self.env['website.menu'].search([('website_product_catag_id', '=', vals.get('parent_id'))])
            values = {}
            if 'name' in vals.keys():
                values['name'] = vals['name']
                result = write_record.write(values)
                write_record.write({"parent_id": parent_record.id})
            else:
                write_record.write({"parent_id": parent_record.id})

        elif 'state' in vals.keys() and search_record:      
            values = {}
            if vals.get('state') == 'inactive':
                values['is_active'] = False
                result = write_record.write(values)
            else:   
                values['is_active'] = True
                result = write_record.write(values) 

        elif 'comment' in vals.keys() and search_record:
            values = {}
            values['comment'] = vals['comment']
            result = write_record.write(values)

        elif 'image' in vals.keys() and search_record:
            values = {}
            values['image'] = vals['image']
            result = write_record.write(values)                        
                
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            write_record = self.env['website.menu'].search([('website_product_catag_id', '=', rec.id)])
            write_record.unlink()
        res = super(WebsiteCategory, self).unlink()
        return res        
