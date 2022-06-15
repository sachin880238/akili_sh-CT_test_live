from odoo import api, fields, models, tools, SUPERUSER_ID, _
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import base64, urllib.request
import logging

class ResUsers(models.Model):
    _inherit = "res.users"

    icon = fields.Char(string="Icon")

    @api.multi
    def create_image(self, val): 
        label = None
        img = False
        size = 90
        apply_logo = self.env['ir.config_parameter'].search([('key','=', 'account_logo.users_icon')])
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
            bk_color_val = self.env['ir.config_parameter'].search([('key','=', 'account_logo.users_icon_background_color')]) 
            tx_color_val = self.env['ir.config_parameter'].search([('key','=', 'account_logo.users_icon_text_color')])
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
            image.save('temp_logo.png')
            imgfile = Image.open("temp_logo.png")
            f = open('temp_logo.png' , 'rb') 
            img = base64.encodestring(f.read()) 
            f.close()
            os.remove('temp_logo.png')
        return img
    
    @api.model
    def create(self, vals):
        if vals.get('image'):
            if not vals.get('icon'):
                name_list = vals['name'].split()
                name_list = [x.lower() for x in name_list]
                if len(name_list) == 1:
                    icon_letter = name_list[0][0:1] 
                else:
                    icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1]
                vals['icon'] = icon_letter.upper()
        elif vals.get('name'):
            icon_letter = None
            if vals.get('icon'):
                icon_letter = vals['icon']
            else:
                name_list = vals['name'].split()
                name_list = [x.lower() for x in name_list]
                if len(name_list) == 1:
                    icon_letter = name_list[0][0:1] 
                else:
                    icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1]
                vals['icon'] = icon_letter.upper()
            vals['image'] = self.create_image(icon_letter) 
        res = super(ResUsers, self).create(vals)
        return res

    @api.one
    def write(self, vals):
        if vals.get('image'):
            res = super(ResUsers, self).write(vals)
            return res
        elif vals.get('icon'):
            vals['image'] = self.create_image(vals['icon'])
        elif vals.get('name'):
            icon_letter = None
            name_list = vals['name'].split()
            if len(name_list) > 1:
                name_list = [x.lower() for x in name_list]
            if len(name_list) == 1:
                icon_letter = name_list[0][0:1] 
            else:
                icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
            vals['icon'] = icon_letter.upper()
            vals['image'] = self.create_image(icon_letter)
        res = super(ResUsers, self).write(vals)               
        return res
