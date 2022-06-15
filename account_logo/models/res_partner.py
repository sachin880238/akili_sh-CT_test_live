from odoo import api, fields, models, _
from odoo.exceptions import UserError
from PIL import Image, ImageOps
from PIL import ImageDraw
from PIL import ImageFont
import os, io
import base64
import string
import random


class ResPartner(models.Model):
    _inherit = "res.partner"

    icon_letters = fields.Char("Icon Letters")

    @api.multi
    def create_image(self, val): 
        label = None
        img = False
        size = 90
        apply_logo = self.env['ir.config_parameter'].search([('key','=', 'account_logo.customers_icon')])
        if not apply_logo.value:
            return None
        if val:
            if len(val) > 2:
                 raise UserError(_('Letters Represent must not be greater then 2 Letters !'))
            else:
                label = val
        if label:
            bk_color = 'gray'
            tx_color = (255,255,0) 
            bk_color_val = self.env['ir.config_parameter'].search([('key','=', 'account_logo.customers_icon_background_color')]) 
            tx_color_val = self.env['ir.config_parameter'].search([('key','=', 'account_logo.customers_icon_text_color')])
            if not bk_color_val and not tx_color_val:
                raise UserError(_('Please Select the Color For Icon First!'))
            if bk_color_val:
                if bk_color_val.value:
                    bk_color = bk_color_val.value 
            if tx_color_val:
                if tx_color_val.value:
                    tx_color = tx_color_val.value 
            label = label.upper() 
            image = Image.new('RGBA', (200, 200))
            draw = ImageDraw.Draw(image)
            draw.ellipse((0, 0, 200, 200), fill = bk_color, outline =bk_color)
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            font = ImageFont.truetype(str(path)+"/font/Roboto-Bold.ttf",size) 
            w, h = draw.textsize(label, font=font)
            draw.text(((200-w)/2,((200-h)/2)-8), label , tx_color, font=font)
            final_string = ''.join((random.choice(string.ascii_uppercase)) for x in range(5)) + '.png'
            image.save(final_string)
            imgfile = Image.open(final_string)
            f = open(final_string, 'rb') 
            img = base64.encodestring(f.read()) 
            f.close()
            os.remove(final_string)
        return img
    
    @api.model
    def create(self, vals):
        if self._context.get('params'):
            if self._context['params'].get('model'):
                if self._context['params']['model'] == 'sale.order' or self._context['params']['model'] == 'purchase.order':
                    if vals.get('image'):
                        res = super(ResPartner, self).create(vals)             
                        return res
                    elif vals.get('icon_letters'):
                        if vals['icon_letters']:
                            vals['image'] = self.create_image(vals['icon_letters'])
                    elif vals.get('name'):
                        icon_letter = None
                        if vals.get('icon_letters'):
                            icon_letter = vals['icon_letters']
                        else:
                            name_list = vals['name'].split()
                            if len(name_list) > 1:
                                if vals.get('company_type') == 'company':
                                    name_list = [x.lower() for x in name_list]
                                    name_list_copy = [x.lower() for x in name_list]
                                    for name in name_list_copy:
                                        if name in ['inc','ltd','pvt','inc.','ltd.','pvt.']:
                                            name_list.remove(name)
                            if len(name_list) == 1:
                                icon_letter = name_list[0][0:1] 
                            else:
                                icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1]
                            vals['icon_letters'] = icon_letter.upper()
                        vals['image'] = self.create_image(icon_letter)
                    res = super(ResPartner, self).create(vals)
                    return res
                elif self._context['params']['model'] == 'res.users':
                    res = super(ResPartner, self).create(vals)
                    return res
                elif self._context['params']['model'] == 'crm.lead':
                    res = super(ResPartner, self).create(vals)
                    return res
                elif self._context['params']['model'] == 'res.partner':
                    if vals.get('name'):
                        icon_letter = None
                        if vals.get('icon_letters'):
                            icon_letter = vals['icon_letters']
                        else:
                            name_list = vals['name'].split()
                            if len(name_list) > 1:
                                if vals.get('company_type') == 'company':
                                    name_list = [x.lower() for x in name_list]
                                    name_list_copy = [x.lower() for x in name_list]
                                    for name in name_list_copy:
                                        if name in ['inc','ltd','pvt','inc.','ltd.','pvt.']:
                                            name_list.remove(name)
                            if len(name_list) == 1:
                                icon_letter = name_list[0][0:1] 
                            else:
                                icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1]
                            vals['icon_letters'] = icon_letter.upper()
                        vals['image'] = self.create_image(icon_letter) 
                    res = super(ResPartner, self).create(vals)
                    return res
                else:
                    res = super(ResPartner, self).create(vals)
                    return res
            else:
                res = super(ResPartner, self).create(vals)
                return res
        else:
            if vals.get('image'):
                res = super(ResPartner, self).create(vals)
            elif vals.get('icon_letters'):
                vals['image'] = self.create_image(vals['icon_letters'])
                res = super(ResPartner, self).create(vals)
            elif vals.get('name'):
                icon_letter = None
                if vals.get('icon_letters'):
                    icon_letter = vals['icon_letters']
                else:
                    name_list = vals['name'].split()
                    if len(name_list) > 1:
                        if vals.get('company_type') == 'company':
                            name_list = [x.lower() for x in name_list]
                            name_list_copy = [x.lower() for x in name_list]
                            for name in name_list_copy:
                                if name in ['inc', 'ltd', 'pvt', 'inc.', 'ltd.', 'pvt.']:
                                    name_list.remove(name)
                    if len(name_list) == 1:
                        icon_letter = name_list[0][0:1]
                    else:
                        icon_letter = name_list[0][0:1] + name_list[len(name_list) - 1][0:1]
                    vals['icon_letters'] = icon_letter.upper()
                vals['image'] = self.create_image(icon_letter)
                res = super(ResPartner, self).create(vals)
            return res

    @api.one
    def write(self, vals):
        if self._context.get('params'):
            if self._context['params'].get('model'):
                if self._context['params']['model'] == 'sale.order' or self._context['params']['model'] == 'sale.order':
                    if vals.get('image'):
                        res = super(ResPartner, self).write(vals)             
                        return res
                    elif vals.get('icon_letters'):
                        if vals['icon_letters']:
                            vals['image'] = self.create_image(vals['icon_letters'])
                    elif vals.get('name') or vals.get('company_type'):
                        icon_letter = None
                        name_list = None
                        if vals.get('name'):
                            name_list = vals['name'].split()
                        else:
                            name_list = self.name.split()
                        if len(name_list) > 1:
                            if not vals.get('company_type'):
                                if self.company_type == 'company':
                                    name_list = [x.lower() for x in name_list]
                                    name_list_copy = [x.lower() for x in name_list]
                                    for name in name_list_copy:
                                        if name in ['inc','ltd','pvt','inc.','ltd.','pvt.']:
                                            name_list.remove(name)
                            else:
                                if vals.get('company_type') == 'company':
                                    name_list = [x.lower() for x in name_list]
                                    name_list_copy = [x.lower() for x in name_list]
                                    for name in name_list_copy:
                                        if name in ['inc','ltd','pvt','inc.','ltd.','pvt.']:
                                            name_list.remove(name)                  
                                    # name_list =  list(set([x.lower() for x in name_list]).difference(['inc','ltd','pvt']))
                        if len(name_list) == 1:
                            icon_letter = name_list[0][0:1] 
                        else:
                            icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1]
                        vals['icon_letters'] = icon_letter.upper()
                        vals['image'] = self.create_image(icon_letter)
                    res = super(ResPartner, self).write(vals)             
                    return res
                elif self._context['params']['model'] == 'res.users':
                    res = super(ResPartner, self).write(vals)
                    return res
                elif self._context['params']['model'] == 'res.partner' or vals.get('is_partner'):
                    if vals.get('image'):
                        res = super(ResPartner, self).write(vals)             
                        return res
                    elif vals.get('icon_letters'):
                        vals['icon_letters'] = vals['icon_letters'].upper()
                        vals['image'] = self.create_image(vals['icon_letters'])
                    elif self.name or self.company_type:
                        icon_letter = None
                        name_list = None
                        if vals.get('name'):
                            name_list = vals['name'].split()
                        else:
                            try:
                              name_list = self.name.split()
                            except:
                              name_list = self.comp_name.split()
                        if len(name_list) > 1:
                            if not vals.get('company_type'):
                                if self.company_type == 'company':
                                    name_list = [x.lower() for x in name_list]
                                    name_list_copy = [x.lower() for x in name_list]
                                    for name in name_list_copy:
                                        if name in ['inc','ltd','pvt','inc.','ltd.','pvt.']:
                                            name_list.remove(name)
                            else:
                                if vals.get('company_type') == 'company':
                                    name_list = [x.lower() for x in name_list]
                                    name_list_copy = [x.lower() for x in name_list]
                                    for name in name_list_copy:
                                        if name in ['inc','ltd','pvt','inc.','ltd.','pvt.']:
                                            name_list.remove(name)                  
                                    # name_list =  list(set([x.lower() for x in name_list]).difference(['inc','ltd','pvt']))
                        if len(name_list) == 1:
                            icon_letter = name_list[0][0:1] 
                        else:
                            icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
                        vals['icon_letters'] = icon_letter.upper()
                        vals['image'] = self.create_image(icon_letter)
                    res = super(ResPartner, self).write(vals)               
                    return res
                else:
                    res = super(ResPartner, self).write(vals)               
                    return res
            else:
                res = super(ResPartner, self).create(vals)
                return res
        else:
            if vals.get('image'):
                res = super(ResPartner, self).write(vals)             
                return res
            elif 'icon_letters' in vals:
                if vals['icon_letters']:
                    vals['image'] = self.create_image(vals['icon_letters'])
            elif vals.get('name') or vals.get('company_type'):
                icon_letter = None
                name_list = None
                if vals.get('name'):
                    name_list = vals['name'].split()
                else:
                    name_list = self.name.split()
                if len(name_list) > 1:
                    if not vals.get('company_type'):
                        if self.company_type == 'company':
                            name_list = [x.lower() for x in name_list]
                            name_list_copy = [x.lower() for x in name_list]
                            for name in name_list_copy:
                                if name in ['inc', 'ltd', 'pvt', 'inc.', 'ltd.', 'pvt.']:
                                    name_list.remove(name)
                    else:
                        if vals.get('company_type') == 'company':
                            name_list = [x.lower() for x in name_list]
                            name_list_copy = [x.lower() for x in name_list]
                            for name in name_list_copy:
                                if name in ['inc', 'ltd', 'pvt', 'inc.', 'ltd.', 'pvt.']:
                                    name_list.remove(name)
                                    # name_list =  list(set([x.lower() for x in name_list]).difference(['inc','ltd','pvt']))
                if len(name_list) == 1:
                    icon_letter = name_list[0][0:1]
                else:
                    icon_letter = name_list[0][0:1] + name_list[len(name_list) - 1][0:1]
                vals['icon_letters'] = icon_letter.upper()
                vals['image'] = self.create_image(icon_letter)
            res = super(ResPartner, self).write(vals)
            return res

    def resize_image(self, image_data):
        try:
            im = Image.open(io.BytesIO(base64.b64decode(image_data)))
            im = im.resize((128, 128));
            bigsize = (im.size[0] * 3, im.size[1] * 3)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(im.size, Image.ANTIALIAS)
            im.putalpha(mask)

            output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            output.save('output.png')
            imgfile = Image.open("output.png")
            f = open('output.png' , 'rb') 
            img = base64.encodestring(f.read())
            f.close()
            os.remove('output.png')
            return img
        except:
            raise UserError(_('Please select only jpeg or png format!!'))

    @api.onchange('image')
    def get_partner_image(self):
        if not self.image:
            if self.icon_letters :
                self.image = self.create_image(self.icon_letters)
            elif self.name:
                icon_letter = None
                name_list = None

                name_list = self.name.split()
                
                if len(name_list) == 1:
                    icon_letter = name_list[0][0:1] 
                else:
                    icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
                self.icon_letters = icon_letter.upper()
                self.image = self.create_image(icon_letter)
        else:
            self.image = self.resize_image(self.image)
