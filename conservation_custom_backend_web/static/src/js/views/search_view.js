odoo.define('conservation_web.search_view', function (require) {
"use strict";
     	
    var Search_view = require('web.SearchView');
    var local_storage = require('web.local_storage');

	Search_view.include({

		init: function() {
	        local_storage.setItem('visible_search_menu', 'true')
	        this._super.apply(this, arguments);
    	},
	})

});
