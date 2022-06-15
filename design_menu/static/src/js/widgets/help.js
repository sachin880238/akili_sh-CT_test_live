odoo.define('help_menu_item.help', function (require) {
"use strict";
var rpc = require('web.rpc');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var Rpc = require('web.rpc');
var Core = require('web.core');
var session = require('web.session');

var help = Widget.extend({
    title:'help_menu',
    img:"far fa-question-circle",
    template:'help.template',
    events: {
        "click": "on_click",
    },
   
    on_click: function (event) {

        var action = parseInt(window.location.href.split('action')[1].split('=')[1])
        var view_type = window.location.href.split('view_type')[1].split('=')[1].split('&')[0]
        var model = window.location.href.split('model')[1].split('=')[1].split('&')[0]
        var res_id = false
        var self = this;
       
        this._rpc({
            model: 'erp.help',
            method: 'my_function',
            args:[action, view_type, model]
        })
        .then(function(res) {
            // debugger
            res_id = res.res_id
            self.do_action({
                name:"Description",
                type: 'ir.actions.act_window',
                res_model: 'erp.help.wizard',
                res_id: res_id,
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context:{}
            });
        });   
 
    },
     
});

SystrayMenu.Items.push(help);
return help;

});
