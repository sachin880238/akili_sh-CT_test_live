odoo.define('custom.chatter_button', function (require) {
"use strict";
var core = require('web.core');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var AbstractAction = require('web.AbstractAction')
var PosBaseWidget = require('point_of_sale.BaseWidget');


var CommentButton = screens.ActionButtonWidget.extend({
    template: 'CommentButton',

    button_click: function(){

    var self = this;
    self.custom_function();
    
    },

    custom_function: function(){
        console.log('Hi I am button click of CustomButton');
        alert("comment")
    }

});

// screens.define_action_button({
//     'name': 'chatter_button',
//     'widget': CommentButton,
// });



});
function openCity(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}
