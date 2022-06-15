odoo.define('web_extend.KanbanRecord', function (require) {
"use strict";

var KanbanRecord = require('web.KanbanRecord');
KanbanRecord.include({
        /**
         * Renders the record
         *
         * @returns {Deferred}
         */
        _render: function () {
            this.defs = [];
            this._replaceElement(this.qweb.render('kanban-box', this.qweb_context));
            var kanban = this.$el.addClass('o_kanban_record').attr("tabindex",0);
            var models = ['res.partner', 'crm.lead']
            if (models.includes(this.modelName)) {
                $('<style>.o_kanban_view.o_kanban_ungrouped .o_kanban_record { width: 350px; }</style>').appendTo(kanban);
            }
            this.$el.attr('role', 'article');
            this.$el.data('record', this);
            if (this.$el.hasClass('oe_kanban_global_click') ||
                this.$el.hasClass('oe_kanban_global_click_edit')) {
                this.$el.on('click', this._onGlobalClick.bind(this));
                this.$el.on('keydown', this._onKeyDownCard.bind(this));
            } else {
                this.$el.on('keydown', this._onKeyDownOpenFirstLink.bind(this));
            }
            this._processFields();
            this._processWidgets();
            this._setupColor();
            this._setupColorPicker();
            this._attachTooltip();

            // We use boostrap tooltips for better and faster display
            this.$('span.o_tag').tooltip({delay: {'show': 50}});

            return $.when.apply(this, this.defs);
        },
    });
});
