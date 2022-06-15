# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WebsiteMenu(models.Model):

    _inherit = "website.menu"
    _order = 'sequence'


    @api.depends('sequence')
    def compute_seuence(self):
        for record in self:
            if record.is_for_catag==True:
                search_record = self.env['website.menu'].search([('is_for_catag', '=', True)])
                parent_record = self.env['website.menu'].search([('website_product_catag_id.parent_id', '=', False),('is_for_child_catag','=',False)])
                if search_record:
                    seq_change = record.sequence
                    for rec in parent_record:
                        if rec:
                            record.arrange_sequece=True
                            rec.write({'sequence':seq_change + 1})
            record.arrange_sequece=True

    is_active = fields.Boolean("Is Active?", default=True)
    underline = fields.Boolean("Underline?")
    is_for_catag = fields.Boolean("Is For Category")
    is_for_child_catag = fields.Boolean("Is For Children Category")
    website_product_catag_id = fields.Many2one('product.public.category')
    arrange_sequece = fields.Boolean("Arrange",compute="compute_seuence",store=True)
    comment = fields.Text('Comment')
    image = fields.Binary("Image")

    sequence = fields.Integer(string='Sequence')

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    dash_icon = fields.Char(string="icon",default='fas fa-dollar-sign')

    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_payment_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_payment_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

class UoM(models.Model):
    _inherit = 'uom.uom'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class WebsitePage(models.Model):
    _inherit ='website.page'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class WebsiteRedirect(models.Model):
    _inherit ='website.redirect'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')


class PaymentToken(models.Model):
    _inherit ='payment.token'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class PurchaseOrder(models.Model):
    _inherit ='purchase.order'

    # _order = 'sequence'
    # sequence = fields.Integer(string='Sequence')
    # dash_icon = fields.Char(string="icon",default='fas fa-rectangle-portrait')

class AccountInvoice(models.Model):
    _inherit ='account.invoice'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class ProductCategory(models.Model):
    _inherit ='product.category'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class StockPicking(models.Model):
    _inherit ='stock.picking'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    dash_icon = fields.Char(string="icon",default='fas fa-truck')


class StockInventory(models.Model):
    _inherit ='stock.inventory'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_inventory_adju_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_inventory_adju_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"


class StockScrap(models.Model):
    _inherit ='stock.scrap'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_scrap_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_scrap_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

class Orderpoint(models.Model):
    _inherit ='stock.warehouse.orderpoint'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')



class ProductProduct(models.Model):
    _inherit = 'product.product'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    dash_icon = fields.Char(string="icon",default='fas fa-truck fa-rotate-180')



class BarcodeNomenclature(models.Model):
    _inherit = 'barcode.nomenclature'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_production_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_production_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_mrp_unbuild_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.depends('parent_state')
    def get_mrp_unbuild_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class AccountIncoterms(models.Model):
    _inherit = 'account.incoterms'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')


class AuthOauthProvider(models.Model):
    _inherit = 'auth.oauth.provider'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class ResLang(models.Model):
    _inherit = 'res.lang'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class Website(models.Model):
    _inherit = 'website'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')


class PosConfig(models.Model):
    _inherit = 'pos.config'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')


class UtmMedium(models.Model):
    _inherit = 'utm.medium'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class UtmSource(models.Model):
    _inherit = 'utm.source'

    order = 'sequence'
    sequence = fields.Integer(string='Sequence')

class Users(models.Model):
    _inherit ='res.users'

    _order = 'sequence'
    sequence = fields.Integer(string='Sequence')

# class StockMove(models.Model):
#     _inherit = "stock.move"

#     _order = 'sequence'
#     sequence = fields.Integer('Sequence')
class Project(models.Model):
    _inherit = "project.project"

    dash_icon = fields.Char(string="icon",default='fas fa-project-diagram')
