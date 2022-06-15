from odoo import api, fields, models, _
from PIL import Image, ImageOps
from PIL import ImageDraw
from PIL import ImageFont
from odoo.exceptions import UserError
import os, io
import base64

class CrmLead(models.Model):
    _inherit = "crm.lead"
   
    lead_icon_letters = fields.Char('Icon', size=2)
    dash_icon = fields.Char(string="icon",default='fas fa-star')
    
    @api.multi
    def create_image(self, val): 
        label = None
        img = False
        size = 90
        apply_logo = self.env['ir.config_parameter'].search([('key','=', 'account_logo.leads_icon')])
        if not apply_logo.value:
            return None
        position = ()
        if val:
            if len(val) > 2:
                 raise UserError(_('Letters Represent must not be greater then 2 Letters !'))
            elif len(val) == 2:
               label = val
               position = (38,44)
               size = 90
            else:
                label = val
                position = (60,35)
                size = 90
        if label:
            bk_color = 'gray'
            tx_color = (255,255,0) 
            bk_color_val = self.env['ir.config_parameter'].search([('key','=', 'account_logo.leads_icon_background_color')]) 
            tx_color_val = self.env['ir.config_parameter'].search([('key','=', 'account_logo.leads_icon_text_color')])
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
        if vals.get('contact_name') or vals.get('company_name') or vals.get('email_from'):
            icon_letter = None

            if vals.get('lead_icon_letters'):
                icon_letter = vals['lead_icon_letters']
            elif vals.get('contact_name'):
                name_list = vals['contact_name'].split()
                if len(name_list) == 1:
                    icon_letter = name_list[0][0:1] 
                else:
                    icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1]
                vals['lead_icon_letters'] = icon_letter.upper()

            elif vals.get('company_name'):
                name_list = vals['company_name'].split()
                if len(name_list) == 1:
                    icon_letter = name_list[0][0:1] 
                else:
                    icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1]
                vals['lead_icon_letters'] = icon_letter.upper()

            elif vals.get('email_from'):
                icon_letter = "@"
                vals['lead_icon_letters'] = icon_letter
                       
            vals['image'] = self.create_image(icon_letter) 
        res = super(CrmLead, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'lead_icon_letters' in vals:
            if vals['lead_icon_letters']:
                vals['image'] = self.create_image(vals['lead_icon_letters'])        
        res = super(CrmLead, self).write(vals)               
        return res

    #GENERATING ICONS FROM FIELD'S VALUE
    @api.onchange('contact_name','company_name','email_from')
    def get_lead_icon(self):
        if self.contact_name:
            icon_letter = None
            name_list = None

            name_list = self.contact_name.split()
            
            if len(name_list) == 1:
                icon_letter = name_list[0][0:1] 
            else:
                icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
            self.lead_icon_letters = icon_letter.upper()
            self.image = self.create_image(icon_letter)

        elif self.company_name:
            icon_letter = None
            name_list = None

            name_list = self.company_name.split()
            
            if len(name_list) == 1:
                icon_letter = name_list[0][0:1] 
            else:
                icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
            self.lead_icon_letters = icon_letter.upper()
            self.image = self.create_image(icon_letter)

        elif self.email_from:
            icon_letter = None
            icon_letter = '@'
            self.lead_icon_letters = icon_letter.upper()
            self.image = self.create_image(icon_letter)
        else:
            icon_letter = None
            self.lead_icon_letters = icon_letter
            self.image = self.create_image(icon_letter)

    @api.onchange('lead_icon_letters')
    def lead_icon_onchange(self):
        if self.lead_icon_letters:
            icon_letter = None
            icon_letter = self.lead_icon_letters
            self.lead_icon_letters = icon_letter.upper()
            self.image = self.create_image(icon_letter)

        elif self.contact_name:
            icon_letter = None
            name_list = None

            name_list = self.contact_name.split()
            
            if len(name_list) == 1:
                icon_letter = name_list[0][0:1] 
            else:
                icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
            self.lead_icon_letters = icon_letter.upper()
            self.image = self.create_image(icon_letter)

        elif self.company_name:
            icon_letter = None
            name_list = None

            name_list = self.company_name.split()
            
            if len(name_list) == 1:
                icon_letter = name_list[0][0:1] 
            else:
                icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
            self.lead_icon_letters = icon_letter.upper()
            self.image = self.create_image(icon_letter)

        elif self.email_from:
            icon_letter = None
            icon_letter = '@'
            self.lead_icon_letters = icon_letter.upper()
            self.image = self.create_image(icon_letter)
        else:
            icon_letter = None
            self.lead_icon_letters = icon_letter
            self.image = self.create_image(icon_letter)

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
            raise UserError(_('Please select only jpeg or png format!'))

    @api.onchange('image')
    def get_lead_image(self):
        if not self.image:
            if self.contact_name:
                icon_letter = None
                name_list = None

                name_list = self.contact_name.split()
                
                if len(name_list) == 1:
                    icon_letter = name_list[0][0:1] 
                else:
                    icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
                self.lead_icon_letters = icon_letter.upper()
                self.image = self.create_image(icon_letter)
            elif self.company_name:
                icon_letter = None
                name_list = None

                name_list = self.company_name.split()
                
                if len(name_list) == 1:
                    icon_letter = name_list[0][0:1] 
                else:
                    icon_letter = name_list[0][0:1] + name_list[len(name_list) -1][0:1] 
                self.lead_icon_letters = icon_letter.upper()
                self.image = self.create_image(icon_letter)
            elif self.email_from:
                icon_letter = None
                self.lead_icon_letters = icon_letter
                self.image = self.create_image(icon_letter)
        else:
            self.image = self.resize_image(self.image)
