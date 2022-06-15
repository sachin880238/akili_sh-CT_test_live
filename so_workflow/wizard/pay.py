from odoo import api, fields, models, _


class AddPayment(models.TransientModel):
    _name = "add.payment"
    _description = "Add Payment"

    @api.onchange('open_acc')
    def onchange_open_acc(self): 
        if not self.currency_id:
            rec = self.env['sale.order'].browse(self._context['active_id'])  
            self.currency_id = rec.currency_id.id 
        if self.open_acc:
            self.c_card = False 
            self.check = False 
            self.bk_transfer = False
            self.cash = False   

    @api.onchange('c_card')
    def onchange_c_card(self): 
        if not self.currency_id:
            rec = self.env['sale.order'].browse(self._context['active_id'])   
            self.currency_id = rec.currency_id.id  
        if self.c_card:
            self.open_acc= False 
            self.check = False 
            self.bk_transfer = False
            self.cash = False  

    @api.onchange('check', 'bk_transfer' , 'cash')
    def onchange_check(self): 
        if not self.currency_id:
            rec = self.env['sale.order'].browse(self._context['active_id'])  
            self.currency_id = rec.currency_id.id   
        if self.check:
            self.c_card = False 
            self.open_acc = False 
            self.bk_transfer = False
            self.cash = False

    @api.onchange('bk_transfer')
    def onchange_bk_transfer(self): 
        if not self.currency_id:
            rec = self.env['sale.order'].browse(self._context['active_id']) 
            self.currency_id = rec.currency_id.id
        if self.bk_transfer:
            self.c_card = False 
            self.check = False 
            self.open_acc = False
            self.cash = False

    @api.onchange('cash')
    def onchange_cash(self):
        if not self.currency_id:
            rec = self.env['sale.order'].browse(self._context['active_id'])   
            self.currency_id = rec.currency_id.id
        if self.cash:
            self.c_card = False 
            self.check = False 
            self.bk_transfer = False
            self.open_acc = False  



    currency_id = fields.Many2one('res.currency', compute='find_match', string='Currency')
    action = fields.Selection([('open', 'Open Account'),('ccard', 'Credit Card'),
                               ('check', 'Check'),('bkt', 'Bank Transfer '), ('cash', 'Cash')], 
                               default = 'open', string='Payment Method: ',)

    total = fields.Float(string='Total')
    pay_apply = fields.Float(string='Payments Applied') 
    bal_due = fields.Float(string='Balance Due') 
    new_pay = fields.Float(string='New Payment') 
    open_acc = fields.Boolean(string='Open Account')
    credit_avl = fields.Float(string='Credit Available')
    c_card = fields.Boolean(string='Credit Card')
    card_id = fields.Many2one('payment.token', string='Card')
    conf = fields.Char(string='Confirmation')
    check = fields.Boolean(string='Check')
    check_type = fields.Char(string='Check Type')
    check_no = fields.Char(string='Check Number')
    check_bank = fields.Char(string='Bank ABA')
    check_bank_acc = fields.Char(string='Bank Account')
    bk_transfer = fields.Boolean(string='Bank Transfer')
    conf = fields.Char(string='Confirmation')
    cash = fields.Boolean(string='Cash')
    env_id = fields.Char(string='Envelope ID') 
    note = fields.Char(string='Note')