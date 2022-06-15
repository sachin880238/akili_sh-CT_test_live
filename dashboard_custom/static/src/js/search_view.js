odoo.define('dashboard_custom.SearchView', function (require) {
"use strict";

var SearchView = require('web.SearchView');

SearchView.include({
	willStart: function () {
        this._super();
        var self = this;
        var def;
        if (!this.options.disable_favorites) {
            def = this.loadFilters(this.dataset, this.action.id).then(function (filters) {
                if (self.action.context) {
                    if (self.action.context.dashboard) {
                        function findFilter(dictionary) {
                            return dictionary['id'] == self.action.context.filter;
                        }
                        self.favorite_filters = [filters.find(findFilter)];
                    }
                    else {
                        self.favorite_filters = filters;
                    }
                }
                else {
                    self.favorite_filters = filters;
                }
            });
        }
        return $.when(this, def);
    },

    set_default_filters: function () {
        var self = this,
            default_custom_filter = this.$buttons && this.favorite_menu && this.favorite_menu.get_default_filter();
        if (!self.options.disable_custom_filters && default_custom_filter){
            this.hasFavorites = true;
            return this.favorite_menu.toggle_filter(default_custom_filter, true);
        }
        if (self.action.context){
            if (self.action.context.dashboard){
                this.hasFavorites = true;
                return this.favorite_menu.toggle_filter(default_custom_filter, true);
            }
        }
        if (!_.isEmpty(this.search_defaults) || this.timeRanges) {
            var inputs = this.search_fields.concat(this.filters, this.groupbys);
            var search_defaults = _.invoke(inputs, 'facet_for_defaults', this.search_defaults);
            var defaultTimeRange = this._searchDefaultTimeRange();
            search_defaults.push(defaultTimeRange);
            return $.when.apply(null, search_defaults).then(function () {
                var facets = _.compact(arguments);
                self.query.reset(facets, {preventSearch: true});
            });
        }
        this.query.reset([], {preventSearch: true});
        return $.when();
    },
});
});