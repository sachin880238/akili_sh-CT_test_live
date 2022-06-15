odoo.define('conservation_web.sidebar', function (require) {
"use strict";

    var core = require('web.core');         	
    var Sidebar = require('web.Sidebar');
    var _t = core._t;


    Sidebar.include({
        init: function() {
            this._super.apply(this, arguments);
            if (window.location.href.indexOf('res.partner') >= 1 || this.__parentedParent.dataset.model == 'res.partner'){
                for(var i = 0; i < this.sections.length-1; i++) {
                    if (this.sections[i].name == 'files'){
                       this.sections.splice(i,1);
                    }
                    
                }
            }   
        },
    })
});
