odoo.define('conservation_custom_backend_web.CustomListRenderer', function (require) {
"use strict";

var core = require('web.core');
var ListRenderer = require('web.ListRenderer');
var Dialog = require('web.Dialog');
var utils = require('web.utils');

ListRenderer.include({
    _renderRows: function () {
        var self = this;
        var $rows = _.map(this.state.data, this._renderRow.bind(this));

        if (this.addCreateLine) {
            var $tr = $('<tr>');
            var colspan = self._getNumberOfCols();

            if (this.handleField) {
                colspan = colspan - 1;
            }

            var $td = $('<td>')
            .attr('colspan', colspan)
            .html('&nbsp;');
            $tr.append($td);
            $rows.push($tr);

            _.each(self.creates, function (create, index) {
                var $a = $('<a href="#" role="button">')
                .attr('data-context', create.context)
                .text(create.string);
                if (index > 0) {
                    $a.addClass('ml16');
                }
                $td.append($a);
            });
        }
        return $rows;
    },

    // Change cross icon in many2many field view			
    _renderRow: function (record, index) {
        var $row = this._super.apply(this, arguments);
        if (this.addTrashIcon) {
            $row.children().last().children().addClass('fa-trash-o').css({'font-size':'medium', 'position':'relative', 'right':'8.5px'}).removeClass('fa-times');
        }
        return $row;
    },

    setRowMode: function (recordID, mode) {
        var self = this;

        // find the record and its row index (handles ungrouped and grouped cases
        // as even if the grouped list doesn't support edition, it may contain
        // a widget allowing the edition in readonly (e.g. priority), so it
        // should be able to update a record as well)
        var record;
        var rowIndex;
        if (this.state.groupedBy.length) {
            rowIndex = -1;
            var count = 0;
            utils.traverse_records(this.state, function (r) {
                if (r.id === recordID) {
                    record = r;
                    rowIndex = count;
                }
                count++;
            });
        } else {
            rowIndex = _.findIndex(this.state.data, {id: recordID});
            record = this.state.data[rowIndex];
        }

        if (rowIndex < 0) {
            return $.when();
        }
        var editMode = (mode === 'edit');

        this.currentRow = editMode ? rowIndex : null;
        var $row = this.$('.o_data_row:nth(' + rowIndex + ')');
        var $tds = $row.children('.o_data_cell');
        var oldWidgets = _.clone(this.allFieldWidgets[record.id]);

        // When switching to edit mode, force the dimensions of all cells to
        // their current value so that they won't change if their content
        // changes, to prevent the view from flickering.
        // We need to use getBoundingClientRect instead of outerWidth to
        // prevent a rounding issue on Firefox.
        if (editMode) {
            $tds.each(function () {
                var $td = $(this);
                $td.css({width: $td[0].getBoundingClientRect().width});
            });
        }

        // Prepare options for cell rendering (this depends on the mode)
        var options = {
            renderInvisible: editMode,
            renderWidgets: editMode,
        };
        options.mode = editMode ? 'edit' : 'readonly';

        // Switch each cell to the new mode; note: the '_renderBodyCell'
        // function might fill the 'this.defs' variables with multiple deferred
        // so we create the array and delete it after the rendering.
        var defs = [];
        this.defs = defs;
        if (this.columns[0]['attrs'].name === 'sequence') {
                this.columns[this.columns.length] = this.columns[0];
                this.columns.shift()
            }
        _.each(this.columns, function (node, colIndex) {
            var $td = $tds.eq(colIndex);
            var $newTd = self._renderBodyCell(record, node, colIndex, options);
            // Widgets are unregistered of modifiers data when they are
            // destroyed. This is not the case for simple buttons so we have to
            // do it here.
            if ($td.hasClass('o_list_button')) {
                self._unregisterModifiersElement(node, recordID, $td.children());
            }

            // For edit mode we only replace the content of the cell with its
            // new content (invisible fields, editable fields, ...).
            // For readonly mode, we replace the whole cell so that the
            // dimensions of the cell are not forced anymore.
            if (editMode) {
                $td.empty().append($newTd.contents());
            } else {
                self._unregisterModifiersElement(node, recordID, $td);
                $td.replaceWith($newTd);
            }
        });
        delete this.defs;

        // Destroy old field widgets
        _.each(oldWidgets, this._destroyFieldWidget.bind(this, recordID));

        // Toggle selected class here so that style is applied at the end
        $row.toggleClass('o_selected_row', editMode);
        $row.find('.o_list_record_selector input').prop('disabled', !record.res_id);

        return $.when.apply($, defs).then(function () {
            // necessary to trigger resize on fieldtexts
            core.bus.trigger('DOM_updated');
        });
    },

    _onRemoveIconClick: function (event) {
        event.stopPropagation();
        var self = this;
        Dialog.confirm(self, _t("Are you sure you want to delete this record ?"), {
            confirm_callback: function () {
                var $row = $(event.target).closest('tr');
                var id = $row.data('id');
                if ($row.hasClass('o_selected_row')) {
                    self.trigger_up('list_record_remove', {id: id});
                }
                else {
                    self.unselectRow().then(function () {
                        self.trigger_up('list_record_remove', {id: id});
                    });
                }
            }
        });
    },
    /**
     * optionally add a th in the header for the remove icon column.
     * @private
     */
    _renderHeader: function () {
        var $thead = this._super.apply(this, arguments);
        if (this.addTrashIcon) {
            $thead.find('tr').append($('<th>', {class: 'o_list_record_remove_header'}));
        }
        return $thead;
    },

    _renderFooter: function () {
        const $footer = this._super.apply(this, arguments);
        if (this.addTrashIcon) {
            $footer.find('tr').append($('<td>'));
        }
        return $footer;
    },
});
});
