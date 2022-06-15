odoo.define('custom.custom_button', function (require) {
"use strict";
var core = require('web.core');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');


var ActionpadWidget = PosBaseWidget.extend({
    template: 'ActionpadWidget',
    init: function(parent, options) {
        var self = this;
        this._super(parent, options);
        this.pos.bind('change:selectedClient', function() {
            self.renderElement();
        });
    },
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.pay').click(function(){
            var order = self.pos.get_order();
            var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                return line.has_valid_product_lot();
            });
            if(!has_valid_product_lot){
                self.gui.show_popup('confirm',{
                    'title': _t('Empty Serial/Lot Number'),
                    'body':  _t('One or more product(s) required serial/lot number.'),
                    confirm: function(){
                        self.gui.show_screen('payment');
                    },
                });
            }else{
                self.gui.show_screen('payment');
            }
        });
        this.$('.set-customer').click(function(){
            self.gui.show_screen('clientlist');
        });
        this.$('.open_wiz').click(function(){
            self.gui.show_screen('clientlist');
        });
    }
});


var PasswordPopupWidget = NumberPopupWidget.extend({
    renderElement: function(){
        this._super();
        this.$('.popup').addClass('popup-password');
    },
    click_numpad: function(event){
        this._super.apply(this, arguments);
        var $value = this.$('.value');
        $value.text($value.text().replace(/./g, '•'));
    },
});

});
