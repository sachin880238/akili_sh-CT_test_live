odoo.define('dashboard_custom.FavoriteMenu', function (require) {
"use strict";

var FavoriteMenu = require('web.FavoriteMenu');

FavoriteMenu.include({
	get_default_filter: function () {
        if (this.action.context) {
            if (this.action.context.dashboard) {
                var personal_filter = _.find(this.filters, function (filter) {
                    return filter.user_id && filter.is_default;
                });
                if (personal_filter) {
                    return personal_filter;
                }
                return _.find(this.filters, function (filter) {
                    return !filter.user_id && filter.is_default;
                });
            }
            else {
                var myObj = this.filters
                var myKeys = Object.keys(myObj)
                var matchingKeys = myKeys.filter(function(key){ return key.indexOf('(false)') !== -1 });
                matchingKeys.forEach(e => delete myObj[e]);

                var personal_filter = _.find(myObj, function (filter) {
                    return filter.user_id && filter.is_default;
                });
                if (personal_filter) {
                    return personal_filter;
                }
                return _.find(myObj, function (filter) {
                    return !filter.user_id && filter.is_default;
                });

            }
        }
        else {
            var myObj = this.filters
            var myKeys = Object.keys(myObj)
            var matchingKeys = myKeys.filter(function(key){ return key.indexOf('(false)') !== -1 });
            matchingKeys.forEach(e => delete myObj[e]);

            var personal_filter = _.find(myObj, function (filter) {
                return filter.user_id && filter.is_default;
            });
            if (personal_filter) {
                return personal_filter;
            }
            return _.find(myObj, function (filter) {
                return !filter.user_id && filter.is_default;
            });

        }
    },

    append_filter: function (filter) {
        var self = this;
        var key = this.key_for(filter);

        if (filter.user_id) {
            this.$user_divider.show();
        } else {
            this.$shared_divider.show();
        }
        if (!(key in this.$filters)) {
            var $filter = $('<div>', {class: 'position-relative'})
                .addClass('o-searchview-custom-private')
                .append($('<a>', {role: 'menuitemradio', href: '#', class: 'dropdown-item'}).text(filter.name))
                .append($('<span>', {
                    class: 'fa fa-trash-o o-remove-filter',
                    on: {
                        click: function (event) {
                            event.stopImmediatePropagation();
                            self.remove_filter(filter, $filter, key);
                        },
                    },
                }))
                .insertBefore(filter.user_id ? this.$user_divider : this.$shared_divider);
            this.$filters[key] = $filter;
        }
        this.$filters[key].unbind('click').click(function () {
            self.toggle_filter(filter);
        });
    },
});
});