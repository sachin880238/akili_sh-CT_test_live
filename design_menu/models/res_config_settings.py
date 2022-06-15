# -*- coding: utf-8 -*-
from odoo import fields, models, api
import os
import getpass


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    align = fields.Boolean(string='Align', default=True)
    theme_color = fields.Char(string='Background Color',size=7)
    header_menu_color = fields.Char(string='Header Menu Color')
    header_bckgrnd_color = fields.Char(string='Header Background Color')
    button_text_color = fields.Char(string='Button Text Color')
    button_bckgrnd_color = fields.Char(string='Button Backgground Color')
    form_button_txt_color = fields.Char(string='Form Button Text Color')
    form_button_bckgrnd_color = fields.Char(string='Form Button Backgroumd Color')

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('header_menu_color', self.header_menu_color)
        self.env['ir.config_parameter'].sudo().set_param('align', self.align)
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['align'] = self.env['ir.config_parameter'].sudo().get_param('align')
        res['header_menu_color'] = self.env['ir.config_parameter'].sudo().get_param('header_menu_color')
        # boolean_object = self.env['system.config'].search([('field_type','=','boolean')])
        # for record in boolean_object:
        #     if record.current_value_boolean:
        #         variant_sale = record.field_name
        #         res[variant_sale] = True
        #     else:
        #         variant_sale = record.field_name
        #         res[variant_sale] = False 

        # integer_object = self.env['system.config'].search([('field_type','=','integer')])
        # for record in integer_object:
        #     if record.current_value_integer:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_integer
        #     else:
        #         variant_sale = record.field_name
        #         res[variant_sale] = 0

        # float_object = self.env['system.config'].search([('field_type','=','float')])
        # for record in float_object:
        #     if record.current_value_float:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_float
        #     else:
        #         variant_sale = record.field_name
        #         res[variant_sale] = 0.0        

        # string_object = self.env['system.config'].search([('field_type','=','string')])
        # for record in string_object:
        #     if record.current_value_char:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_char
        #     else:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_char

        # date_object = self.env['system.config'].search([('field_type','=','date')])
        # for record in date_object:
        #     if record.current_value_date:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_date
        #     else:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_date

        # time_object = self.env['system.config'].search([('field_type','=','time')])
        # for record in time_object:
        #     if record.current_value_time:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_time
        #     else:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_time

        # text_object = self.env['system.config'].search([('field_type','=','text')])
        # for record in text_object:
        #     if record.current_value_text:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_text
        #     else:
        #         variant_sale = record.field_name
        #         res[variant_sale] = record.current_value_text        
        return res


class SystemConfigSettings(models.Model):
    _name = 'system.config'
    _order = 'sequence'
    _rec_name = 'name'
    _inherit = 'ir.module.module'


    app_name = fields.Char(string="Application", readonly=True)
    cat_name = fields.Char(string="Category", readonly=True)
    field_name = fields.Char(string="Field Name")
    field_type = fields.Char(string="Type", readonly=True)
    source = fields.Char(string="Source", readonly=True) 
    comment = fields.Char(string="Comment", readonly=True)
    default_value_boolean = fields.Boolean(string="Default Value", readonly=True)
    default_value_integer = fields.Integer(string="Default Value", readonly=True)
    default_value_float = fields.Float(string="Default Value", readonly=True)
    default_value_char = fields.Char(string="Default Value", readonly=True)
    default_value_text = fields.Text(string="Default Value", readonly=True)
    default_value_selection = fields.Selection([], string="Default Value", readonly=True)
    default_value_date = fields.Date(string="Default Value", readonly=True)
    default_value_time = fields.Datetime(string="Default Value", readonly=True)
    default_value_color = fields.Char(string="Default Value", readonly=True)
    current_value_boolean = fields.Boolean(string="Current Value")
    current_value_integer = fields.Integer(string="Current Value")
    current_value_float = fields.Float(string="Current Value")
    current_value_char = fields.Char(string="Current Value")
    current_value_text = fields.Text(string="Current Value")
    current_value_selection = fields.Selection([], string="Current Value")
    current_value_date = fields.Date(string="Current Value")
    current_value_time = fields.Datetime(string="Current Value")
    virtual_value = fields.Boolean(string="Virtual Value", default=False)
    current_multi_sales_price_method = fields.Selection([
        ('percentage', 'Multiple prices per product (e.g. customer segments, currencies)'),
        ('formula', 'Prices computed from formulas (discounts, margins, roundings)')
        ], default='formula', string="Current Value")
    current_auth_signup_uninvited = fields.Selection([
        ('b2b', 'On invitation'),
        ('b2c', 'Free sign up'),
    ], string='Current Value', default='b2c', config_parameter='auth_signup.invitation_scope')
    current_default_invoice_policy = fields.Selection([
        ('order', 'Invoice what is ordered'),
        ('delivery', 'Invoice what is delivered')
        ], 'Current Value',
        default='order',
        default_model='product.template')
    current_default_purchase_method = fields.Selection([
        ('purchase', 'Ordered quantities'),
        ('receive', 'Delivered quantities'),
        ], string="Current Value", default_model="product.template",
        help="This default value is applied to any new product created. "
        "This can be changed in the product detail form.", default="receive")
    current_module_procurement_jit = fields.Selection([
        ('1', 'Immediately after sales order confirmation'),
        ('0', 'Manually or based on automatic scheduler')
        ], "Current Value",
        help="Reserving products manually in delivery orders or by running the scheduler is advised to better manage priorities in case of long customer lead times or/and frequent stock-outs.")
    current_default_picking_policy = fields.Selection([
        ('direct', 'Ship products as soon as available, with back orders'),
        ('one', 'Ship all products at once')
        ], "Current Value", default='direct', default_model="sale.order", required=True)
    current_product_weight_in_lbs = fields.Selection([
        ('0', 'Kilogram'),
        ('1', 'Pound'),
    ], 'Current Value', config_parameter='product.weight_in_lbs', default='0')
    default_multi_sales_price_method = fields.Selection([
        ('percentage', 'Multiple prices per product (e.g. customer segments, currencies)'),
        ('formula', 'Prices computed from formulas (discounts, margins, roundings)')
        ], default='formula', string="Default Value", readonly=True)
    default_auth_signup_uninvited = fields.Selection([
        ('b2b', 'On invitation'),
        ('b2c', 'Free sign up'),
    ], string='Default Value', default='b2c', config_parameter='auth_signup.invitation_scope', readonly=True)
    default_default_invoice_policy = fields.Selection([
        ('order', 'Invoice what is ordered'),
        ('delivery', 'Invoice what is delivered')
        ], 'Default Value',
        default='order',
        default_model='product.template', readonly=True)
    default_default_purchase_method = fields.Selection([
        ('purchase', 'Ordered quantities'),
        ('receive', 'Delivered quantities'),
        ], string="Default Value", default_model="product.template",
        help="This default value is applied to any new product created. "
        "This can be changed in the product detail form.", default="receive", readonly=True)
    default_module_procurement_jit = fields.Selection([
        ('1', 'Immediately after sales order confirmation'),
        ('0', 'Manually or based on automatic scheduler')
        ], "Default Value",
        help="Reserving products manually in delivery orders or by running the scheduler is advised to better manage priorities in case of long customer lead times or/and frequent stock-outs.", readonly=True)
    default_default_picking_policy = fields.Selection([
        ('direct', 'Ship products as soon as available, with back orders'),
        ('one', 'Ship all products at once')
        ], "Default Value", default='direct', default_model="sale.order", readonly=True)
    default_product_weight_in_lbs = fields.Selection([
        ('0', 'Kilogram'),
        ('1', 'Pound'),
    ], 'Default Value', config_parameter='product.weight_in_lbs', default='0', readonly=True)

    sequence= fields.Integer(string="Sequence")
    state = fields.Selection([('default', 'Default'), ('custom', 'Custom')], string='Status', required=True, readonly=True, copy=False, default='default')
    name = fields.Char(string="Name",readonly=True)
    curr_enable = fields.Boolean(string="Enable")
    curr_selection =fields.Selection([(' ', ' ')],string="Selection")
    curr_link = fields.Selection([(' ', ' ')], string="Link")
    curr_text = fields.Char(string="Text")
    curr_color = fields.Char(string="Color")
    curr_color_value = fields.Char(string="Color Value")
    curr_integer = fields.Integer(string="Integer")
    curr_deciml = fields.Float(string="Decimal")
    def_enable = fields.Boolean(string="Enable")
    def_selection = fields.Selection([(' ',' ')],string="Selection")
    def_link = fields.Selection([(' ',' ')],string="Link")
    def_text = fields.Char(string="Text")
    def_color = fields.Char(string="Color")
    def_color_value = fields.Char(string="Default Value")
    def_integer = fields.Integer(string="Integer")
    def_decimal = fields.Float(string="Decimal")

    color_application = fields.Selection([('','')], string="Selection")
    color_field_name = fields.Selection([('','')], string="Field Name")
    c_type = fields.Char(string="Type")
    is_editable = fields.Boolean(string="Editable")
    desc = fields.Text(string="Description")

    #sales field
    group_product_variant             = fields.Boolean('Variants and Options')
    group_uom                         = fields.Boolean('Units of Measure')
    module_product_email_template     = fields.Boolean('Deliver Content by Email')
    group_stock_packaging             = fields.Boolean('Product Packagings')
    group_discount_per_so_line        = fields.Boolean('Discounts')
    multi_sales_price                 = fields.Boolean('Multiple Sales Prices per Product')
    multi_sales_price_method = fields.Selection([
        ('percentage', 'Multiple prices per product (e.g. customer segments, currencies)'),
        ('formula', 'Prices computed from formulas (discounts, margins, roundings)')
        ], default='percentage', string="Pricelists Method")
    auth_signup_uninvited = fields.Selection([
        ('b2b', 'On invitation'),
        ('b2c', 'Free sign up'),
    ], string='Customer Account', default='b2b', config_parameter='auth_signup.invitation_scope')
    module_sale_margin = fields.Boolean("Margins")
    portal_confirmation_sign = fields.Boolean( string='Online Signature', readonly=False)
    portal_confirmation_pay = fields.Boolean( string='Online Payment', readonly=False)
    group_sale_delivery_address = fields.Boolean("Customer Addresses", implied_group='sale.group_delivery_invoice_address')
    use_sale_note = fields.Boolean(
        string='Default Terms & Conditions',
        oldname='default_use_sale_note',
        config_parameter='sale.use_sale_note')
    sale_note = fields.Text( string="Terms & Conditions", readonly=False)
    use_quotation_validity_days = fields.Boolean("Default Quotation Validity", config_parameter='sale.use_quotation_validity_days')
    group_warning_sale = fields.Boolean("Sale Order Warnings", implied_group='sale.group_warning_sale')
    auto_done_setting = fields.Boolean("Lock Confirmed Sales", config_parameter='sale.auto_done_setting')
    group_proforma_sales = fields.Boolean(string="Pro-Forma Invoice", implied_group='sale.group_proforma_sales',
        help="Allows you to send pro-forma invoice.")
    quotation_validity_days = fields.Integer( string="Default Quotation Validity (Days)", readonly=False)
    module_delivery = fields.Boolean("Shipping Costs")
    module_delivery_dhl = fields.Boolean("DHL Connector")
    module_delivery_fedex = fields.Boolean("FedEx Connector")
    module_delivery_ups = fields.Boolean("UPS Connector")
    module_delivery_usps = fields.Boolean("USPS Connector")
    module_delivery_bpost = fields.Boolean("bpost Connector")
    module_delivery_easypost = fields.Boolean("Easypost Connector")
    group_sale_order_dates = fields.Boolean("Delivery Date", implied_group='sale.group_sale_order_dates')
    default_invoice_policy = fields.Selection([
        ('order', 'Invoice what is ordered'),
        ('delivery', 'Invoice what is delivered')
        ], 'Invoicing Policy',
        default='order',
        default_model='product.template')
    automatic_invoice = fields.Boolean("Automatic Invoice",
                                       help="The invoice is generated automatically and available in the customer portal "
                                            "when the transaction is confirmed by the payment acquirer.\n"
                                            "The invoice is marked as paid and the payment is registered in the payment journal "
                                            "defined in the configuration of the payment acquirer.\n"
                                            "This mode is advised if you issue the final invoice at the order and not after the delivery.",
                                       config_parameter='sale.automatic_invoice')
    template_id = fields.Many2one('mail.template', 'Email Template',
                                  domain="[('model', '=', 'account.invoice')]",
                                  config_parameter='sale.default_email_template',
                                  )


    deposit_default_product_id = fields.Many2one(
        'product.product',
        'Deposit Product',
        domain="[('type', '=', 'service')]",
        config_parameter='sale.default_deposit_product_id',
        oldname='default_deposit_product_id',
        help='Default product used for payment advances')
    taxt_email = fields.Html(string="Text", compute='_get_default_text', inverse='_set_default_text', store=True)


    
    @api.depends('name')
    def _get_default_text(self):
        for record in self:
            if record.name == "Website Header Icon Call Config Setting":
                text = "<div><p style='margin-bottom: 6px;'>US: 410-366-1146</p><p>International: (+1) 410-366-1146</p><br/></div>"
                if record.taxt_email != False and record.taxt_email != text:
                    record.taxt_email = record.taxt_email
                else:
                    record.taxt_email = text
            elif record.name == "Website Header Icon Email Config Setting":
                text = "<p><t>For questions about ordering or specifying<br/> our products for current or future projects,<br/>please email:</t></p><p class='text-center'><a href='mailto:sales@conservationtechnology.com' style='color: #1e77c5'><i>sales@conservationtechnology.com</i></a></p><p><t>For questions or comments relating to an<br/>existing quotation, order, invoice, or customer service ticket, please find the document here:</t></p><p class='text-center'><a href='mailto:support@conservationtechnology.com' style='color: #1e77c5'><i>Your Account</i></a></p><p/><br/>"
                if record.taxt_email != False and record.taxt_email != text:
                    record.taxt_email = record.taxt_email
                else:
                    record.taxt_email = text
            else:
                record.taxt_email = False
    
    def _set_default_text(self):
        for record in self:
            record.name = record.name

    mail_header_color = fields.Char(string="Color")
    main_heading_email = fields.Char(string="Header content")
    web_header_bckgrnd_color = fields.Char(string="Header Background Color")
    web_header_content_color = fields.Char(string="Header Content Color")

    @api.onchange('def_enable')
    def onchange_default(self):
        if self.def_enable==False:
            self.curr_enable=True
        if self.def_enable==True:
            self.curr_enable=False

    @api.onchange('curr_enable')
    def onchange_current(self):
        if self.curr_enable==False:
            self.def_enable=True
        if self.curr_enable==True:
            self.def_enable=False

    @api.onchange('curr_color')
    def onchange_color_value(self):
        if self.curr_color:
            self.curr_color_value = self.curr_color

    @api.onchange('curr_color_value')
    def onchange_curr_color_value(self):
        if self.curr_color_value:
            self.curr_color = self.curr_color_value

    @api.multi
    def reset_colors(self):
        absolute_path = os.path.dirname(os.path.abspath(__file__))
        user_name=getpass.getuser()
        dir_path = '/home/'+user_name
        if self.name=="Header Content Color":
            self.write({'def_color_value':"#863a3a",'def_color':"#863a3a",'def_enable':True,'curr_enable':False})
        if self.name=="Header Background Color":
            self.write({'def_color_value':"#F5F4F0",'def_color':"#F5F4F0",'def_enable':True,'curr_enable':False})
        if self.name=="Header Rollover Color":
            self.write({'def_color_value':"#deded0",'def_color':"#deded0",'def_enable':True,'curr_enable':False})
                            
    @api.model
    def create(self,vals):
        absolute_path = os.path.dirname(os.path.abspath(__file__))
        user_name=getpass.getuser()
        dir_path = '/home/'+user_name
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".scss"):
                    path = os.path.join(root, file)
                    if file == 'primary_variables.scss' and ".local/share" not in path and 'conservation_custom_backend_web' in path:
                        fobj = open(os.path.join(root, file))
                        text = fobj.read()
                        with open(os.path.join(root, file), 'r') as file:
                            # read a list of lines into data
                            data = file.readlines()
                        if vals['name']=="Header Content Color":
                            data[6]="$o-community-menu-color: "+"#863a3a"+";\n"
                            data[7] = "$o-font-color: " + "#863a3a" + ";\n"
                            with open(path, 'w') as file:
                                file.writelines(data)
                            vals["def_color_value"]="#863a3a"
                            vals["def_color"]="#863a3a"
                        if vals['name']=="Header Background Color":
                            data[5] = '$o-community-color: ' + "#F5F4F0" + ";\n"
                            with open(path, 'w') as file:
                                file.writelines(data)
                            vals["def_color_value"]="#F5F4F0"
                            vals["def_color"]="#F5F4F0"
                        if vals['name']=="Header Rollover Color":
                            data[10]=" $header-content-hover: "+"#deded0"+";\n"
                            with open(path, 'w') as file:
                                file.writelines(data)
                            vals["def_color_value"]="#deded0"
                            vals["def_color"]="#deded0"
        res = super(SystemConfigSettings, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'current_value_boolean' in vals.keys():
            if vals.get('current_value_boolean') != self.default_value_boolean:
                self.state = 'custom'
            else:
                self.state = 'default'
        if 'current_value_integer' in vals.keys():
            if vals.get('current_value_integer') != self.default_value_integer:
                self.state = 'custom'
            else:
                self.state = 'default'
        if 'current_value_float' in vals.keys():
            if vals.get('current_value_float') != self.default_value_float:
                self.state = 'custom'
            else:
                self.state = 'default'
        if 'current_value_char' in vals.keys():
            if vals.get('current_value_char') != self.default_value_char:
                self.state = 'custom'
            else:
                self.state = 'default'
        if 'current_value_date' in vals.keys():
            if vals.get('current_value_date') != self.default_value_date:
                self.state = 'custom'
            else:
                self.state = 'default'
        if 'current_value_time' in vals.keys():
            if vals.get('current_value_time') != self.default_value_time:
                self.state = 'custom'
            else:
                self.state = 'default'
        if 'current_value_text' in vals.keys():
            if vals.get('current_value_text') != self.default_value_text:
                self.state = 'custom'
            else:
                self.state = 'default'                                                                                    
        # print("+++++++++++++++++++++@+++++++++++++++++++++", self.default_value_boolean,vals)
        if self.name not in ('Sale Config Setting','Website Header Icon Email Config Setting','Website Header Icon Call Config Setting'):
            absolute_path = os.path.dirname(os.path.abspath(__file__))
            user_name=getpass.getuser()
            dir_path = '/home/'+user_name
            if "curr_enable" in vals and vals['curr_enable']==True:
                vals['state']="custom"
            if "def_enable" in vals and vals['def_enable']==True:
                vals['state']="default"
            res = super(SystemConfigSettings, self).write(vals)
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(".scss"):
                        path = os.path.join(root, file)
                        if file == 'primary_variables.scss' and ".local/share" not in path and 'conservation_custom_backend_web' in path:
                            fobj = open(os.path.join(root, file))
                            text = fobj.read()
                            with open(os.path.join(root, file), 'r') as file:
                                # read a list of lines into data
                                data = file.readlines()
                            if self.name=="Header Content Color":
                                if self.curr_enable==True:
                                    data[6]="$o-community-menu-color: "+self.curr_color_value+";\n"
                                    data[7] = "$o-font-color: " + self.curr_color_value + ";\n"
                                    with open(path, 'w') as file:
                                        file.writelines(data)
                                else:
                                    data[6]="$o-community-menu-color: "+"#863a3a"+";\n"
                                    data[7] = "$o-font-color: " + "#863a3a" + ";\n"
                                    with open(path, 'w') as file:
                                        file.writelines(data)
                                    
                                    

                            if self.name=="Header Background Color":
                                if self.curr_enable==True:
                                    if self.curr_enable==True:
                                        data[5]="$o-community-color: "+self.curr_color_value+";\n"
                                        vals['curr_enable']=True
                                        with open(path, 'w') as file:
                                            file.writelines(data)


                                else:
                                    data[5] = '$o-community-color: ' + "#F5F4F0" + ";\n"
                                    with open(path, 'w') as file:
                                        file.writelines(data)
                                    

                            if self.name=="Header Rollover Color":
                                if self.curr_enable==True:
                                    data[10]=" $header-content-hover: "+self.curr_color_value+";\n"
                                    vals['curr_enable']=True
                                    with open(path, 'w') as file:
                                        file.writelines(data)
                                else:
                                    data[10]=" $header-content-hover: "+"#deded0"+";\n"
                                    with open(path, 'w') as file:
                                        file.writelines(data)



                        if file == 'primary_variables.scss' and ".local/share" not in path and 'website_custom_menu' in path:
                            fobj = open(os.path.join(root, file))
                            text = fobj.read()
                            with open(os.path.join(root, file), 'r') as file:
                                # read a list of lines into data
                                data = file.readlines()
                            if self.name=="Website Header Color Config Setting":
                                data[5]="$o-web-icon-arrow-color: "+self.web_header_bckgrnd_color+";\n"
                                with open(path, 'w') as file:
                                    file.writelines(data)
                                                        
                                    
        else:
            res = super(SystemConfigSettings, self).write(vals)
        return res



    
