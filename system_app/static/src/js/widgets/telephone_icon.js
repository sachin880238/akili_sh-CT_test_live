odoo.define('help_menu_item.telephone_icon', function (require) {
"use strict";
var rpc = require('web.rpc');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var Rpc = require('web.rpc');
var Core = require('web.core');
var session = require('web.session');

var telephone = Widget.extend({
    title:'phone details',
    img:"fas fa-exchange",
    template:'telephone.template',
    events: {
        "click": "on_click",
    },

    on_click: function (event) {
        var url_dict = {}
        var fetch_url = window.location.href.split('#')[1].split('&')
        for(var val in fetch_url) {
            if (fetch_url[val].split('=')[0] == 'model' || fetch_url[val].split('=')[0] == 'view_type'){
                url_dict[fetch_url[val].split('=')[0]] = fetch_url[val].split('=')[1]
            }else{
                url_dict[fetch_url[val].split('=')[0]] = parseInt(fetch_url[val].split('=')[1])
            }
        }     
        var res_id = false
        var action_name = false

        var self = this;
       
        this._rpc({
            model: 'erp.help',
            method: 'fetch_help',
            args:[url_dict]
        })
        .then(function(res) {
            res_id = res.res_id
            action_name = res.action_name
            if(!action_name){
                self.do_action({
                        name:"Help:No Action",  
                        type: 'ir.actions.act_window',
                        res_model: 'erp.help.wizard',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        context:{'default_have_action':action_name,'url_dict':url_dict,
                        'default_description':'<h3 style="text-align: center;"><b><font style="background-color: rgb(247, 247, 247); color: rgb(255, 0, 0); font-size: 36px;">Description Not Found Their is No Action</font></b></h3>'}
                });

            }else{ 
                if(res_id){
                    self.do_action({
                        name:"Help: " + action_name,  
                        type: 'ir.actions.act_window',
                        res_model: 'erp.help.wizard',
                        res_id: res_id,
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        context:{'default_res_model':action_name,'url_dict':url_dict,}
                    });

                }else{
                    self.do_action({
                        name:"Help: " + action_name,  
                        type: 'ir.actions.act_window',
                        res_model: 'erp.help.wizard',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        context:{'url_dict':url_dict,'default_description':'<h3 style="text-align: center;"><b><font style="background-color: rgb(247, 247, 247); color: rgb(0, 209, 156); font-size: 36px;">Description Not Found</font></b></h3>'}
                    });
                }
            }
            
        });   
 
    },
     
});

SystrayMenu.Items.push(telephone);
return telephone;

});
