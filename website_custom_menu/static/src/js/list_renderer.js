odoo.define('web.ListRenderer', function (require) {
"use strict";

var BasicRenderer = require('web.BasicRenderer');
var config = require('web.config');
var core = require('web.core');
var dom = require('web.dom');
var field_utils = require('web.field_utils');
var Pager = require('web.Pager');
var utils = require('web.utils');
var QWeb = core.qweb;

var _t = core._t;

// Allowed decoration on the list's rows: bold, italic and bootstrap semantics classes
var DECORATIONS = [
    'decoration-bf',
    'decoration-it',
    'decoration-danger',
    'decoration-info',
    'decoration-muted',
    'decoration-primary',
    'decoration-success',
    'decoration-warning'
];

var FIELD_CLASSES = {
    float: 'o_list_number',
    integer: 'o_list_number',
    monetary: 'o_list_number',
    text: 'o_list_text',
};

var HEADING_COLUMNS_TO_SKIP_IN_GROUPS = 2;

var ListRenderer = BasicRenderer.extend({
    events: {
        'click tbody tr': '_onRowClicked',
        'click tbody .o_list_record_selector': '_onSelectRecord',
        'click thead th.o_column_sortable': '_onSortColumn',
        'click .o_group_header': '_onToggleGroup',
        'click thead .o_list_record_selector input': '_onToggleSelection',
        'keypress thead tr td': '_onKeyPress',
        'keydown tr': '_onKeyDown',
        'keydown thead tr': '_onKeyDown',
        
    },
    /**
     * @constructor
     * @param {Widget} parent
     * @param {any} state
     * @param {Object} params
     * @param {boolean} params.hasSelectors
     */
    init: function (parent, state, params) {
        this._super.apply(this, arguments);
        // This attribute lets us know if there is a handle widget on a field,
        // and on which field it is set.
        this.handleField = null;
        this.action_id=params.action_id
        this.button_add=false
        this.check_type=0
        this._processColumns(params.columnInvisibleFields || {});
        this.rowDecorations = _.chain(this.arch.attrs)
            .pick(function (value, key) {
                return DECORATIONS.indexOf(key) >= 0;
            }).mapObject(function (value) {
                return py.parse(py.tokenize(value));
            }).value();
        this.hasSelectors = params.hasSelectors;
        this.selection = params.selectedRecords || [];
        this.pagers = []; // instantiated pagers (only for grouped lists)
        this.editable = params.editable;
        this.isGrouped = this.state.groupedBy.length > 0;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------
    /**
     * Order to focus to be given to the content of the current view
     * @override
     * @public
     */
    giveFocus: function () {
        this.$('tbody .o_list_record_selector input:first()').focus();
    },
    /**
     * @override
     */
    updateState: function (state, params) {
        this.isGrouped = state.groupedBy.length > 0;
        this._processColumns(params.columnInvisibleFields || {});
        if (params.selectedRecords) {
            this.selection = params.selectedRecords;
        }
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * This method does a in-memory computation of the aggregate values, for
     * each columns that corresponds to a numeric field with a proper aggregate
     * function.
     *
     * The result of these computations is stored in the 'aggregate' key of each
     * column of this.columns.  This will be then used by the _renderFooter
     * method to display the appropriate amount.
     *
     * @private
     */
    _computeAggregates: function () {
        var self = this;
        var data = [];
        if (this.selection.length) {
            utils.traverse_records(this.state, function (record) {
                if (_.contains(self.selection, record.id)) {
                    data.push(record); // find selected records
                }
            });
        } else {
            data = this.state.data;
        }
        
        _.each(this.columns, this._computeColumnAggregates.bind(this, data));
    },
    /**
     * Compute the aggregate values for a given column and a set of records.
     * The aggregate values are then written, if applicable, in the 'aggregate'
     * key of the column object.
     *
     * @private
     * @param {Object[]} data a list of selected/all records
     * @param {Object} column
     */
    _computeColumnAggregates: function (data, column) {
        var attrs = column.attrs;
        var field = this.state.fields[attrs.name];
        if (!field) {
            return;
        }
        var type = field.type;
        if (type !== 'integer' && type !== 'float' && type !== 'monetary') {
            return;
        }
        var func = (attrs.sum && 'sum') || (attrs.avg && 'avg') ||
            (attrs.max && 'max') || (attrs.min && 'min');
        if (func) {
            var count = 0;
            var aggregateValue = (func === 'max') ? -Infinity : (func === 'min') ? Infinity : 0;
            _.each(data, function (d) {
                count += 1;
                var value = (d.type === 'record') ? d.data[attrs.name] : d.aggregateValues[attrs.name];
                if (func === 'avg') {
                    aggregateValue += value;
                } else if (func === 'sum') {
                    aggregateValue += value;
                } else if (func === 'max') {
                    aggregateValue = Math.max(aggregateValue, value);
                } else if (func === 'min') {
                    aggregateValue = Math.min(aggregateValue, value);
                }
            });
            if (func === 'avg') {
                aggregateValue = count ? aggregateValue / count : aggregateValue;
            }
            column.aggregate = {
                help: attrs[func],
                value: aggregateValue,
            };
        }
    },
    /**
     * return the number of visible columns.  Note that this number depends on
     * the state of the renderer.  For example, in editable mode, it could be
     * one more that in non editable mode, because there may be a visible 'trash
     * icon'.
     *
     * @private
     * @returns {integer}
     */
    _getNumberOfCols: function () {
        var n = this.columns.length;
        return this.hasSelectors ? n + 1 : n;
    },
    /**
     * Removes the columns which should be invisible.
     *
     * @param  {Object} columnInvisibleFields contains the column invisible modifier values
     */
    _processColumns: function (columnInvisibleFields) {
        var self = this;
        self.handleField = null;
        this.columns = _.reject(this.arch.children, function (c) {
            if (c.tag === 'control') {
                return true;
            }
            var reject = c.attrs.modifiers.column_invisible;
            // If there is an evaluated domain for the field we override the node
            // attribute to have the evaluated modifier value.
            if (c.attrs.name in columnInvisibleFields) {
                reject = columnInvisibleFields[c.attrs.name];
            }
            if (!reject && c.attrs.widget === 'handle') {
                self.handleField = c.attrs.name;
            }
            return reject;
        });
    },
    /**
     * Render a list of <td>, with aggregates if available.  It can be displayed
     * in the footer, or for each open groups.
     *
     * @private
     * @param {any} aggregateValues
     * @param {Boolean} isHeader indicates wheter the groups rendered are on the header or on the footer
     * @returns {jQueryElement[]} a list of <td> with the aggregate values
     */
    _renderAggregateCells: function (aggregateValues, isHeader) {
        var self = this;
        
        return _.map(this.columns, function (column, index) {
            if (isHeader  && index === 0) {
                return;
            }
            var $cell = $('<td>');
            if (config.debug) {
                $cell.addClass(column.attrs.name);
            }
            if (column.attrs.name in aggregateValues) {
                var field = self.state.fields[column.attrs.name];
                var value = aggregateValues[column.attrs.name].value;
                var help = aggregateValues[column.attrs.name].help;
                var formatFunc = field_utils.format[column.attrs.widget];
                if (!formatFunc) {
                    formatFunc = field_utils.format[field.type];
                }
                var formattedValue = formatFunc(value, field, { escape: true });
                $cell.addClass('o_list_number').attr('title', help).html(formattedValue);
            }
            return $cell;
        });
    },
    /**
     * Render the main body of the table, with all its content.  Note that it
     * has been decided to always render at least 4 rows, even if we have less
     * data.  The reason is that lists with 0 or 1 lines don't really look like
     * a table.
     *
     * @private
     * @returns {jQueryElement} a jquery element <tbody>
     */
    _renderBody: function () {
        var $rows = this._renderRows();
        while ($rows.length < 4) {
            $rows.push(this._renderEmptyRow());
        }
        return $('<tbody>').append($rows);
    },
    /**
     * Render a cell for the table. For most cells, we only want to display the
     * formatted value, with some appropriate css class. However, when the
     * node was explicitely defined with a 'widget' attribute, then we
     * instantiate the corresponding widget.
     *
     * @private
     * @param {Object} record
     * @param {Object} node
     * @param {integer} colIndex
     * @param {Object} [options]
     * @param {Object} [options.mode]
     * @param {Object} [options.renderInvisible=false]
     *        force the rendering of invisible cell content
     * @param {Object} [options.renderWidgets=false]
     *        force the rendering of the cell value thanks to a widget
     * @returns {jQueryElement} a <td> element
     */
    _renderBodyCell: function (record, node, colIndex, options) {
        var tdClassName = 'o_data_cell';
        if (node.tag === 'button') {
            tdClassName += ' o_list_button';
        } else if (node.tag === 'field') {
            var typeClass = FIELD_CLASSES[this.state.fields[node.attrs.name].type];
            if (typeClass) {
                tdClassName += (' ' + typeClass);
            }
            if (node.attrs.widget) {
                tdClassName += (' o_' + node.attrs.widget + '_cell');
            }
        }
        var $td = $('<td>', { class: tdClassName });

        // We register modifiers on the <td> element so that it gets the correct
        // modifiers classes (for styling)
        var modifiers = this._registerModifiers(node, record, $td, _.pick(options, 'mode'));
        // If the invisible modifiers is true, the <td> element is left empty.
        // Indeed, if the modifiers was to change the whole cell would be
        // rerendered anyway.
        if (modifiers.invisible && !(options && options.renderInvisible)) {
            return $td;
        }

        if (node.tag === 'button') {
            return $td.append(this._renderButton(record, node));
        } else if (node.tag === 'widget') {
            return $td.append(this._renderWidget(record, node));
        }
        if (node.attrs.widget || (options && options.renderWidgets)) {
            var $el = this._renderFieldWidget(node, record, _.pick(options, 'mode'));
            this._handleAttributes($el, node);
            return $td.append($el);
        }
        var name = node.attrs.name;
        var field = this.state.fields[name];
        var value = record.data[name];
        var formattedValue = field_utils.format[field.type](value, field, {
            data: record.data,
            escape: true,
            isPassword: 'password' in node.attrs,
            digits: node.attrs.digits ? JSON.parse(node.attrs.digits) : undefined,
        });
        this._handleAttributes($td, node);
        return $td.html(formattedValue);
    },
    /**
     * Renders the button element associated to the given node and record.
     *
     * @private
     * @param {Object} record
     * @param {Object} node
     * @returns {jQuery} a <button> element
     */
    _renderButton: function (record, node) {
        var self = this;
        var $button = this._renderButtonFromNode(node, {
            extraClass: node.attrs.icon ? 'o_icon_button' : undefined,
            textAsTitle: !!node.attrs.icon,
        });
        this._handleAttributes($button, node);
        this._registerModifiers(node, record, $button);

        if (record.res_id) {
            // TODO this should be moved to a handler
            $button.on("click", function (e) {
                e.stopPropagation();
                self.trigger_up('button_clicked', {
                    attrs: node.attrs,
                    record: record,
                });
            });
        } else {
            if (node.attrs.options.warn) {
                $button.on("click", function (e) {
                    e.stopPropagation();
                    self.do_warn(_t("Warning"), _t('Please click on the "save" button first.'));
                });
            } else {
                $button.prop('disabled', true);
            }
        }

        return $button;
    },
    /**
     * Render a complete empty row.  This is used to fill in the blanks when we
     * have less than 4 lines to display.
     *
     * @private
     * @returns {jQueryElement} a <tr> element
     */
    _renderEmptyRow: function () {
        var $td = $('<td>&nbsp;</td>').attr('colspan', this._getNumberOfCols());
        return $('<tr>').append($td);
    },
    /**
     * Render the footer.  It is a <tfoot> with a single row, containing all
     * aggregates, if applicable.
     *
     * @private
     * @returns {jQueryElement} a <tfoot> element
     */
    _renderFooter: function () {
        var aggregates = {};
        _.each(this.columns, function (column) {
            if ('aggregate' in column) {
                aggregates[column.attrs.name] = column.aggregate;
            }
        });
        var $cells = this._renderAggregateCells(aggregates, false);
        if (this.hasSelectors && this.addTrashIcon === undefined) {
            $cells.unshift($('<td>'));
        }
        return $('<tfoot>').append($('<tr>').append($cells));
    },
    /**
     * Renders the pager for a given group
     *
     * @private
     * @param {Object} group
     * @returns {JQueryElement} the pager's $el
     */
    _renderGroupPager: function (group) {
        var pager = new Pager(this, group.count, group.offset + 1, group.limit);
        pager.on('pager_changed', this, function (newState) {
            var self = this;
            pager.disable();
            this.trigger_up('load', {
                id: group.id,
                limit: newState.limit,
                offset: newState.current_min - 1,
                on_success: function (reloadedGroup) {
                    _.extend(group, reloadedGroup);
                    self._renderView();
                },
                on_fail: pager.enable.bind(pager),
            });
        });
        // register the pager so that it can be destroyed on next rendering
        this.pagers.push(pager);

        var fragment = document.createDocumentFragment();
        pager.appendTo(fragment); // starts the pager
        return pager.$el;
    },
    /**
     * Render the row that represent a group
     *
     * @private
     * @param {Object} group
     * @param {integer} groupLevel the nesting level (0 for root groups)
     * @returns {jQueryElement} a <tr> element
     */
    _renderGroupRow: function (group, groupLevel) {
        var aggregateValues = _.mapObject(group.aggregateValues, function (value) {
            return { value: value };
        });
        var $cells = this._renderAggregateCells(aggregateValues, true);
        var name = group.value === undefined ? _t('Undefined') : group.value;
        var groupBy = this.state.groupedBy[groupLevel];
        if (group.fields[groupBy.split(':')[0]].type !== 'boolean') {
            name = name || _t('Undefined');
        }
        var $th = $('<th>')
            .addClass('o_group_name')
            .text(name + ' (' + group.count + ')');
        if (this.hasSelectors) {
            $th.attr('colspan', HEADING_COLUMNS_TO_SKIP_IN_GROUPS);
        }
        var $arrow = $('<span>')
            .css('padding-left', (groupLevel * 20) + 'px')
            .css('padding-right', '5px')
            .addClass('fa');
        if (group.count > 0) {
            $arrow.toggleClass('fa-caret-right', !group.isOpen)
                .toggleClass('fa-caret-down', group.isOpen);
        }
        $th.prepend($arrow);
        if (group.isOpen && !group.groupedBy.length && (group.count > group.data.length)) {
            var $pager = this._renderGroupPager(group);
            var $lastCell = $cells[$cells.length - 1] || $th;
            $lastCell.addClass('o_group_pager').append($pager);
        }
        return $('<tr>')
            .addClass('o_group_header')
            .toggleClass('o_group_open', group.isOpen)
            .toggleClass('o_group_has_content', group.count > 0)
            .data('group', group)
            .append($th)
            .append($cells);
    },
    /**
     * Render all groups in the view.  We assume that the view is in grouped
     * mode.
     *
     * Note that each group is rendered inside a <tbody>, which contains a group
     * row, then possibly a bunch of rows for each record.
     *
     * @private
     * @param {Object} data the dataPoint containing the groups
     * @param {integer} [groupLevel=0] the nesting level. 0 is for the root group
     * @returns {jQueryElement[]} a list of <tbody>
     */
    _renderGroups: function (data, groupLevel) {
        var self = this;
        groupLevel = groupLevel || 0;
        var result = [];
        var $tbody = $('<tbody>');
        _.each(data, function (group) {
            if (!$tbody) {
                $tbody = $('<tbody>');
            }
            $tbody.append(self._renderGroupRow(group, groupLevel));
            if (group.data.length) {
                result.push($tbody);
                // render an opened group
                if (group.groupedBy.length) {
                    // the opened group contains subgroups
                    result = result.concat(self._renderGroups(group.data, groupLevel + 1));
                } else {
                    // the opened group contains records
                    var $records = _.map(group.data, function (record) {
                        return self._renderRow(record);
                    });
                    result.push($('<tbody>').append($records));
                }
                $tbody = null;
            }
        });
        if ($tbody) {
            result.push($tbody);
        }
        return result;
    },
    /**
     * Render the main header for the list view.  It is basically just a <thead>
     * with the name of each fields
     *
     * @private
     * @param {boolean} isGrouped
     * @returns {jQueryElement} a <thead> element
     */
    _renderHeader: function (isGrouped) {
        if (!isGrouped && this.columns[0]['attrs'].name === 'sequence') {
            this.columns[this.columns.length] = this.columns[0];
            this.columns.shift()
        }
        if (isGrouped && this.columns[0]['attrs'].name === 'sequence') {
            this.columns.shift()
        }
        var $tr = $('<tr>')
            .append(_.map(this.columns, this._renderHeaderCell.bind(this)));
        if (this.hasSelectors) {
            $tr.prepend(this._renderSelector('th'));
        }
        if (!this.hasSelectors) {
            if (this.columns[0]['attrs']['name'] === 'default_address') {
                $tr.children().first().attr('style', 'padding-left: 1.1rem !important; width: 1px')
            }
            else {
                $tr.children().first().attr('style', 'padding-left: 1.1rem !important')
            }
        }
        return $('<thead>').append($tr);
    },
    /**
     * Render a single <th> with the informations for a column. If it is not a
     * field, the th will be empty. Otherwise, it will contains all relevant
     * information for the field.
     *
     * @private
     * @param {Object} node
     * @returns {jQueryElement} a <th> element
     */
    _renderHeaderCell: function (node) {
        var name = node.attrs.name;
        var order = this.state.orderedBy;
        var isNodeSorted = order[0] && order[0].name === name;
        var field = this.state.fields[name];
        var field2 = this.state.fields[name];
        var field3 = this.state.page;
        var $th = $('<th>');
        if (!field) {
            return $th;
        }
        var description;
        if (node.attrs.widget) {
            description = this.state.fieldsInfo.list[name].Widget.prototype.description;
        }
        if (description === undefined) {
            description = node.attrs.string || field.string;
        }
        $th.text(description)
            .data('name', name)
            .toggleClass('o-sort-down', isNodeSorted ? !order[0].asc : false)
            .toggleClass('o-sort-up', isNodeSorted ? order[0].asc : false)
            .addClass(field.sortable && 'o_column_sortable');

        if (isNodeSorted) {
            $th.attr('aria-sort', order[0].asc ? 'ascending' : 'descending');
        }

        if (field.type === 'float' || field.type === 'integer' || field.type === 'monetary') {
            $th.addClass('o_list_number_th');
        }

        // if (field.string === 'sequence' || field.string === 'Sequence' ) {
        //     $th.addClass('fa fa-arrows-v');
        //     $th.removeClass('o_column_sortable');
        // }
      
      

        if (config.debug) {
            var fieldDescr = {
                field: field,
                name: name,
                string: description || name,
                record: this.state,
                attrs: node.attrs,
            };
            this._addFieldTooltip(fieldDescr, $th);
        }
        return $th;
    },
    /**
     * Render a row, corresponding to a record.
     *
     * @private
     * @param {Object} record
     * @returns {jQueryElement} a <tr> element
     */
    _renderRow: function (record) {
        var self = this;
        this.defs = []; // TODO maybe wait for those somewhere ?
        var $cells = _.map(this.columns, function (node, index) {
            return self._renderBodyCell(record, node, index, { mode: 'readonly' });
        });
        delete this.defs;

        var $tr = $('<tr/>', { class: 'o_data_row' })
            .data('id', record.id)
            .append($cells);
        if (this.hasSelectors) {
            $tr.prepend(this._renderSelector('td', !record.res_id));
        }
        if (!this.hasSelectors) {
            $tr.children().first().attr('style', 'padding-left: 1.1rem !important')
        }
        this._setDecorationClasses(record, $tr);
        return $tr;
    },
    /**
     * Render all rows. This method should only called when the view is not
     * grouped.
     *
     * @private
     * @returns {jQueryElement[]} a list of <tr>
     */
    _renderRows: function () {
        return _.map(this.state.data, this._renderRow.bind(this));
    },
    /**
     * A 'selector' is the small checkbox on the left of a record in a list
     * view.  This is rendered as an input inside a div, so we can properly
     * style it.
     *
     * Note that it takes a tag in argument, because selectors in the header
     * are renderd in a th, and those in the tbody are in a td.
     *
     * @private
     * @param {string} tag either th or td
     * @param {boolean} disableInput if true, the input generated will be disabled
     * @returns {jQueryElement}
     */
    _renderSelector: function (tag, disableInput) {
        var $content = dom.renderCheckbox();
        if (disableInput) {
            $content.find("input[type='checkbox']").prop('disabled', disableInput);
        }
        return $('<' + tag + ' width="1">')
            .addClass('o_list_record_selector')
            .append($content);
    },
    /**
     * Main render function for the list.  It is rendered as a table. For now,
     * this method does not wait for the field widgets to be ready.
     *
     * @override
     * @private
     * returns {Deferred} this deferred is resolved immediately
     */
    _renderView: function () {
        var self = this;
        if( this.check_type!=2){
            
        delete this['creates']; 
    }
    else{
        this.creates=[]
        this.creates.push({'string': "Add a line"});
    }
        this.$el
            .removeClass('table-responsive')
            .empty();

        // destroy the previously instantiated pagers, if any
        _.invoke(this.pagers, 'destroy');
        this.pagers = [];
        var $table = $('<table>').addClass('o_list_view table table-sm table-hover table-striped');
        this.$el.addClass('table-responsive')
            .append($table);
        this._computeAggregates();
        $table.toggleClass('o_list_view_grouped', this.isGrouped);
        $table.toggleClass('o_list_view_ungrouped', !this.isGrouped);
        this.hasHandle = this.state.orderedBy.length === 0 ||
            this.state.orderedBy[0].name === this.handleField;
        console.log("ggggggggggggggggggggggggggg",this.action_id)
        var self=this
         
        var action_id=this.action_id
        var model_name=this.state.model
        if(self.editable != 'bottom'){
        self._rpc({
                    model: 'ak.backend.listview',
                    method: 'custom_get_status_field',
                    args:[action_id,model_name]
                }).then(function (return_data) {
                    console.log("222222222222222222222222",return_data)
                    var count=0

        self.columns = _.reject(self.columns, function (c) {
            count=count+1
            console.log("------------===========",return_data.length,c)
            var field_count=0
            var i;
            for (i = 0; i < return_data.length; ++i) {
                console.log("------------->>>>>",return_data)
                if(c.attrs.name == return_data[i][0]){
                    field_count=field_count+1
                    console.log("iiiiiiiiiiiiiiiiiiii")
                    return return_data[i][1];
                }
            }
            console.log("hhhhhhhhhhhhhhhhhhhhhhhhhh")
            // if (c.tag === 'control') {
            //     return true;
            // }
            // var reject = c.attrs.modifiers.column_invisible;
            // // If there is an evaluated domain for the field we override the node
            // // attribute to have the evaluated modifier value.
            // if (c.attrs.name in columnInvisibleFields) {
            //     reject = columnInvisibleFields[c.attrs.name];
            // }
            // if (!reject && c.attrs.widget === 'handle') {
            //     self.handleField = c.attrs.name;
            // }
            // // if (c.attrs.name == 'country_id'){
            // //     return true
            // // }
        //     if(field_count == 0){
        //     if(c.attrs.name === 'street_address'){
        //         if (c.tag === 'control') {
        //             return true;
        //         }
        //         var reject = c.attrs.modifiers.column_invisible;
        //         // If there is an evaluated domain for the field we override the node
        //         // attribute to have the evaluated modifier value.
        //         if (c.attrs.name in columnInvisibleFields) {
        //             reject = [];
        //         }
        //         if (!reject && c.attrs.widget === 'handle') {
        //             self.handleField = c.attrs.name;
        //         }
        //         // if (c.attrs.name == 'country_id'){
        //         //     return true
        //         // }
        //     }
        // }
            // return reject;
        });
                

        if (self.isGrouped) {
            $table
                .append(self._renderHeader(true))
                .append(self._renderGroups(self.state.data))
                .append(self._renderFooter());
        } else {
            $table
                .append(self._renderHeader())
                .append(self._renderBody())
                .append(self._renderFooter());
        }
        if (self.selection.length) {
            var $checked_rows = self.$('tr').filter(function (index, el) {
                return _.contains(self.selection, $(el).data('id'));
            });
            $checked_rows.find('.o_list_record_selector input').prop('checked', true);
        }
        self.hsp_editable_btn = $(' <i id="select_columns"  class="oe_select_columns fas fa-ellipsis-v" data-toggle="dropdown" aria-expanded="false" style="right: 20px;z-index: 1;top: 3px;position: absolute;text-align: center;line-height: 30px;cursor: pointer;text-align: center;padding-left: 4px;"/><ul id="show-menu" class="dropdown-menu o_group_by_menu oe_dropdown_menu" role="menu"style="max-height: 250px;overflow: auto;position: absolute;will-change: transform;top: 0px;width: 154px;left: -35px !important;transform: translate3d(1689px, 33px, 0px);"></ul></div>')
            self.hsp_editable_btn.appendTo(self.$buttons)
            var last_th=self.$el.find( 'table thead tr th:last')
            $(last_th[0]).removeClass("o_column_sortable");
            $(last_th[0]).append(self.hsp_editable_btn);
        var count=0
        if(self.__parentedParent.attrs!= undefined && self.button_add==false){
            $(self.hsp_editable_btn).remove();
            self.hsp_editable_btn = $(' <i id="select_columns"  class="oe_select_columns fas fa-ellipsis-v" data-toggle="dropdown" aria-expanded="false" style="right: 17px;z-index: 1;top: 3px;position: absolute;text-align: center;line-height: 30px;cursor: pointer;text-align: center;padding-left: 4px;"/><ul id="show-menu" class="dropdown-menu o_group_by_menu oe_dropdown_menu" role="menu"style="max-height: 250px;overflow: auto;position: absolute;will-change: transform;top: 0px;width: 154px;left: -35px !important;transform: translate3d(1689px, 33px, 0px);"></ul></div>')
            count=1
            $(last_th[0]).append(self.hsp_editable_btn);
            $(self.editable_hsp_editable_btn).remove();
            self.editable_hsp_editable_btn = $('<div class="icon_change" style="text-align: end;"><button type="button" style="color: #1e77c5;font-size: 25px;position: absolute;top: 55%;left: 95%;" class="oe_edit_only btn btn-secondary fas fa-edit hsp_editable_btn" style="position: relative;"></button></div>')
          $(self.$el).prev().children().last().append(self.editable_hsp_editable_btn);
          self.editable_hsp_editable_btn.on('click', '.hsp_editable_btn', self._make_editbale_click.bind(self));
          
        }
        else{
            count=2
            self.hsp_editable_btn.on('click', '.o_checkbox_editable input', self.editable_bottom.bind(self)); 
        self.hsp_editable_btn.on('click', '.o_checkbox_not_editable input', self.not_editable_bottom.bind(self));
        }
        self.hsp_editable_btn.on('click', '.oe_select_columns', self.my_setup_columns.bind(self));
        self.hsp_editable_btn.on('click', '.o_checkbox input', self.hide_show_columns.bind(self));
        self.hsp_editable_btn.on('click', '.oe_dropdown_menu', self.stop_event.bind(self));
        
    
        if (self.hsp_editable_btn) {
            self.contents = self.hsp_editable_btn[1]
            var columns = []
            _.each(self.arch.children, function(node) {
                var name = node.attrs.name
                var description = undefined
                if (self.state.fields[name]) {
                    description = self.state.fields[name].string
                }
                else {
                    description = node.attrs.string;
                }
                var field_count=0
                var status_invisible;
                for (var i = 0; i < return_data.length; ++i) {

                    if(node.attrs.name == return_data[i][0]){
                        field_count=field_count+1
                        status_invisible=return_data[i][1];
                    }
                }
                columns.push({
                    'field_name': node.attrs.name,
                    'label': description,
                    'invisible': status_invisible || node.attrs.modifiers.column_invisible || false
                })
            })
            var status_editable;
            var not_status_editable;
            $(self.contents).html(QWeb.render('ColumnSelectionDropDowncustom', {
                widget: self,
                count:count,
                columns: columns,
                
            }));
            console.log("hhhhhhhhhjjjjjjjjjjjjjjjjjj")
            // $(self.contents).html(QWeb.render('ColumnSelectionDropDown', {
            //     widget: self,
            //     count:count,
            //     columns: columns,
                
            // }));
            
            
            
        }
    });

}
else{
    if (this.isGrouped) {
            $table
                .append(this._renderHeader(true))
                .append(this._renderGroups(this.state.data))
                .append(this._renderFooter());
        } else {
            $table
                .append(this._renderHeader())
                .append(this._renderBody())
                .append(this._renderFooter());
        }
        if (this.selection.length) {
            var $checked_rows = this.$('tr').filter(function (index, el) {
                return _.contains(self.selection, $(el).data('id'));
            });
            $checked_rows.find('.o_list_record_selector input').prop('checked', true);
        }
        
        
          
        // appending button to div 
       this.hsp_editable_btn = $(' <i id="select_columns"  class="oe_select_columns fas fa-ellipsis-v" data-toggle="dropdown" aria-expanded="false" style="right: 20px;z-index: 1;top: 3px;position: absolute;text-align: center;line-height: 30px;cursor: pointer;text-align: center;padding-left: 4px;"/><ul id="show-menu" class="dropdown-menu o_group_by_menu oe_dropdown_menu" role="menu"style="max-height: 250px;overflow: auto;position: absolute;will-change: transform;top: 0px;width: 154px;left: -35px !important;transform: translate3d(1689px, 33px, 0px);"></ul></div>')
            this.hsp_editable_btn.appendTo(this.$buttons)
            var last_th=this.$el.find( 'table thead tr th:last')
            $(last_th[0]).removeClass("o_column_sortable");
            $(last_th[0]).append(this.hsp_editable_btn);
        var count=0
        if(this.__parentedParent.attrs!= undefined && this.button_add==false){
            $(this.hsp_editable_btn).remove();
            this.hsp_editable_btn = $(' <i id="select_columns"  class="oe_select_columns fas fa-ellipsis-v" data-toggle="dropdown" aria-expanded="false" style="right: 17px;z-index: 1;top: 3px;position: absolute;text-align: center;line-height: 30px;cursor: pointer;text-align: center;padding-left: 4px;"/><ul id="show-menu" class="dropdown-menu o_group_by_menu oe_dropdown_menu" role="menu"style="max-height: 250px;overflow: auto;position: absolute;will-change: transform;top: 0px;width: 154px;left: -35px !important;transform: translate3d(1689px, 33px, 0px);"></ul></div>')
            count=1
            $(last_th[0]).append(this.hsp_editable_btn);
            $(this.editable_hsp_editable_btn).remove();
            this.editable_hsp_editable_btn = $('<div class="icon_change" style="text-align: end;"><button type="button" style="color: #1e77c5;font-size: 25px;position: absolute;top: 55%;left: 95%;" class="oe_edit_only btn btn-secondary fas fa-edit hsp_editable_btn" style="position: relative;"></button></div>')
          $(this.$el).prev().children().last().append(this.editable_hsp_editable_btn);
          this.editable_hsp_editable_btn.on('click', '.hsp_editable_btn', this._make_editbale_click.bind(this));
          
        }
        else{
            count=2
            this.hsp_editable_btn.on('click', '.o_checkbox_editable input', this.editable_bottom.bind(this)); 
        this.hsp_editable_btn.on('click', '.o_checkbox_not_editable input', this.not_editable_bottom.bind(this));
        }
        

        // self.$el[0].appendChild(button); ; 
        this._super();
        
        this.hsp_editable_btn.on('click', '.oe_select_columns', this.my_setup_columns.bind(this));
        this.hsp_editable_btn.on('click', '.o_checkbox input', this.hide_show_columns.bind(this));
        this.hsp_editable_btn.on('click', '.oe_dropdown_menu', this.stop_event.bind(this));
        
        // this.$buttons.on('click', '.oe_dropdown_btn', this.hide_show_columns.bind(this));
        // this.$buttons.on('click', '.oe_dropdown_menu', this.stop_event.bind(this));
        if (this.hsp_editable_btn) {
            this.contents = this.hsp_editable_btn[1]
            var columns = []
            _.each(this.arch.children, function(node) {
                var name = node.attrs.name
                var description = undefined
                if (self.state.fields[name]) {
                    description = self.state.fields[name].string
                }
                else {
                    description = node.attrs.string;
                }
                columns.push({
                    'field_name': node.attrs.name,
                    'label': description,
                    'invisible': node.attrs.modifiers.column_invisible || false
                })
            })
            var status_editable;
            var not_status_editable;
        //     if(this.editable == 'bottom'){
        //     status_editable=false
        //     not_status_editable=true
        // }
        // else{

        //     status_editable=true
        //     not_status_editable=false
        // }
            $(this.contents).html(QWeb.render('ColumnSelectionDropDowncustom', {
                widget: this,
                count:count,
                columns: columns,
                // status_editable:status_editable,
                // not_status_editable:not_status_editable
            }));
        }
}
console.log("fffffffffffffffffffffkkk")
        tableDragger($table[0]);
        
        
          
        // appending button to div 
       
        
        

        // this._super();
        console.log("----------------------->>>gggggggggg")
        
        return this._super();
    },
    my_setup_columns: function() {
        $("#show-menu").show();
    },
    setup_columns: function(action_id) {
        var self = this;
        var fields_data=[]
        _.each($(this.hsp_editable_btn[1]).find('li.item_column'), function(item) {
            var checkbox_item = $(item).find('input');
            var field = _.find(self.arch.children, function(field) {
                return field.attrs.name === checkbox_item.data('name')
            });
            if (checkbox_item.prop('checked')) {
                fields_data.push([self.state.model,false,field.attrs.name,action_id])
                field.attrs.modifiers.column_invisible = false;
                
                
                
            } else {
                fields_data.push([self.state.model,true,field.attrs.name,action_id])
                field.attrs.modifiers.column_invisible = true;
               
            }
            })
        self._rpc({
                    model: 'ak.backend.listview',
                    method: 'custom_get_view_id',
                    args:[fields_data]
                }).then(function (action) {
                    _.each($(self.hsp_editable_btn[1]).find('li.item_column'), function(item) {
            var checkbox_item = $(item).find('input');
            var field = _.find(self.arch.children, function(field) {
                return field.attrs.name === checkbox_item.data('name')
            });
            if (checkbox_item.prop('checked')) {
                fields_data.push([self.state.model,false,field.attrs.name,action_id])
                field.attrs.modifiers.column_invisible = false;
                
                
                
            } else {
                fields_data.push([self.state.model,true,field.attrs.name,action_id])
                field.attrs.modifiers.column_invisible = true;
               
            }
            })
                });
    },
    stop_event: function(e) {
        e.stopPropagation();
    },
    hide_show_columns: function() {
        // $("#show-menu").hide();
        var action_id=this.action_id
        this.setup_columns(action_id)
        if(this.__parentedParent.handle!= undefined ){
        var state = this.__parentedParent.model.get(this.__parentedParent.handle);
        this.updateState(state, {
            reload: true
        })
    }
    else{
        this.updateState(this.__parentedParent.value, {
            reload: true
        })
    }
    },
    /**
     * Each line can be decorated according to a few simple rules. The arch
     * description of the list may have one of the decoration-X attribute with
     * a domain as value.  Then, for each record, we check if the domain matches
     * the record, and add the text-X css class to the element.  This method is
     * concerned with the computation of the list of css classes for a given
     * record.
     *
     * @private
     * @param {Object} record a basic model record
     * @param {jQueryElement} $tr a jquery <tr> element (the row to add decoration)
     */
    _setDecorationClasses: function (record, $tr) {
        _.each(this.rowDecorations, function (expr, decoration) {
            var cssClass = decoration.replace('decoration', 'text');
            $tr.toggleClass(cssClass, py.PY_isTrue(py.evaluate(expr, record.evalContext)));
        });
    },
    /**
     * Update the footer aggregate values.  This method should be called each
     * time the state of some field is changed, to make sure their sum are kept
     * in sync.
     *
     * @private
     */
    _updateFooter: function () {
        this._computeAggregates();
        this.$('tfoot').replaceWith(this._renderFooter());
    },
    /**
     * Whenever we change the state of the selected rows, we need to call this
     * method to keep the this.selection variable in sync, and also to recompute
     * the aggregates.
     *
     * @private
     */
    _updateSelection: function () {
        var $selectedRows = this.$('tbody .o_list_record_selector input:checked')
            .closest('tr');
        this.selection = _.map($selectedRows, function (row) {
            return $(row).data('id');
        });
        this.trigger_up('selection_changed', { selection: this.selection });
        this._updateFooter();
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Manages the keyboard events on the list. If the list is not editable, when the user navigates to
     * a cell using the keyboard, if he presses enter, enter the model represented by the line
     *
     * @private
     * @param {KeyboardEvent} e
     */
    _onKeyDown: function (e) {
        if (!this.editable) {
            switch (e.which) {
                case $.ui.keyCode.DOWN:
                    $(e.currentTarget).next().find('input').focus();
                    e.preventDefault();
                    break;
                case $.ui.keyCode.UP:
                    $(e.currentTarget).prev().find('input').focus();
                    e.preventDefault();
                    break;
                case $.ui.keyCode.ENTER:
                    e.preventDefault();
                    var id = $(e.currentTarget).data('id');
                    if (id) {
                        this.trigger_up('open_record', { id: id, target: e.target });
                    }
                    break;
            }
        }
    },
    /**
     * @private
     * @param {MouseEvent} event
     */
    _onRowClicked: function (event) {
        // The special_click property explicitely allow events to bubble all
        // the way up to bootstrap's level rather than being stopped earlier.
        if (!$(event.target).prop('special_click')) {
            var id = $(event.currentTarget).data('id');
            if (id) {
                this.trigger_up('open_record', { id: id, target: event.target });
            }
        }
    },
    /**
     * @private
     * @param {MouseEvent} event
     */
    _onSelectRecord: function (event) {
        event.stopPropagation();
        this._updateSelection();
        if (!$(event.currentTarget).find('input').prop('checked')) {
            this.$('thead .o_list_record_selector input').prop('checked', false);
        }
    },
    /**
     * @private
     * @param {MouseEvent} event
     */
    _onSortColumn: function (event) {
        var name = $(event.currentTarget).data('name');
        this.trigger_up('toggle_column_order', { id: this.state.id, name: name });
    },
    /**
     * @private
     * @param {MouseEvent} event
     */
    _onToggleGroup: function (event) {
        var group = $(event.currentTarget).data('group');
        if (group.count) {
            this.trigger_up('toggle_group', { group: group });
        }
    },
    /**
     * When the user clicks on the 'checkbox' on the left of a record, we need
     * to toggle its status.
     *
     * @private
     * @param {MouseEvent} event
     */
    _onToggleSelection: function (event) {
        var checked = $(event.currentTarget).prop('checked') || false;
        this.$('tbody .o_list_record_selector input:not(":disabled")').prop('checked', checked);
        this._updateSelection();
    },
    _make_editbale_click: function () {
        var button=this.hsp_editable_btn[0].getElementsByTagName("button")[0];
        if(this.editable == 'bottom'){
            this.editable=false
            this.check_type=1
            this.button_add=true
            this._renderView();
            $(event.target).attr('class', 'btn btn-secondary fa fa-edit hsp_editable_btn')
            
        }
        else{
            $(event.target).attr('class', 'btn btn-secondary fa fa-external-link hsp_editable_btn')
            // button.classList.remove('fa-th');
            // button.classList.add('fa-square');
            this.editable='bottom'
            this.check_type=2
            this.button_add=true
            this._renderView();
        }
    },
    editable_bottom: function (event) {
        // var button=this.hsp_editable_btn[0].getElementsByTagName("button")[0];
        var button=this.hsp_editable_btn[1].getElementsByClassName("o_checkbox_not_editable")[0].getElementsByTagName('input')[0];
        if($(event.target).is(':checked') == true){
            this.editable='bottom'
            button.checked = false;
        }
        if($(event.target).is(':checked') == false){
            this.editable=false
            button.checked = true;
        }
        
    },
     not_editable_bottom: function (event) {
        var button=this.hsp_editable_btn[1].getElementsByClassName("o_checkbox_editable")[0].getElementsByTagName('input')[0];
        if($(event.target).is(':checked') == true){
            this.editable=false
            button.checked = false;
        }
        if($(event.target).is(':checked') == false){
            this.editable='bottom'
            button.checked = true;
        }
        
        
    },
});

return ListRenderer;
});
