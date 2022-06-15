odoo.define('web.o2m_selectable', function (require) {
"use strict";

	var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
	var field_registry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var ListController = require('web.ListController');
    var ActWindowActionManager = require('web.ActionManager');
    var Context = require('web.Context');
    var data = require('web.data');
    // var AbstractField = require('web.AbstractField');
    // var FormView = require('web.FormView');
    var FormRenderer = require('web.FormRenderer');
    var BasicRenderer = require('web.BasicRenderer');
    // var FormController = require('web.FormController');
    var KanbanRenderer = require('web.KanbanRenderer');


    
    ActWindowActionManager.include({
        _onExecuteAction: function(ev){
            var actionData = ev.data.action_data;
            var def = $.Deferred();
            // based on view_manager.js
            if (actionData.type === "object") {
                // ev.stopPropagation();
                var env = ev.data.env;
                var self = this;
                var controller = this.getCurrentController().widget;
              
                var context = new Context(env.context, actionData.context || {});
                var recordID = env.currentID || null;
                var args = recordID ? [[recordID]] : [env.resIDs];
                if (actionData.args) {
                    try {
                        // warning: quotes and double quotes problem due to json and xml clash
                        // maybe we should force escaping in xml or do a better parse of the args array
                        var additionalArgs = JSON.parse(actionData.args.replace(/'/g, '"'));
                        args = args.concat(additionalArgs);
                    } catch (e) {
                        console.error("Could not JSON.parse arguments", actionData.args);
                    }
                }
                var renderer = controller.renderer;
                if (renderer !== undefined){
                    if (renderer.o2mHolder !== undefined){
                        var holder = renderer.o2mHolder;
                        var keys = Object.keys(holder);

                        var o2m = {}
                        for (var i = 0; i < keys.length; i++){
                            var key = keys[i];
                            var rows = []
                            var selectedHandles = holder[key].data.selection;
                            var ids = []
                            for (var index in selectedHandles){
                                var handle = selectedHandles[index];
                                var record = controller.model.get(handle, {raw: true});
                                var recordData = record.data;
                                rows.push(recordData);
                                ids.push(recordData['id'])
                            }
                            o2m[key] = {'ids': ids, 'rows': rows};
                        }

                        context.add({'o2m_selection': o2m});
                    }
                }
                args.push(context.eval());
                def = this._rpc({
                    route: '/web/dataset/call_button',
                    params: {
                        args: args,
                        method: actionData.name,
                        model: env.model,
                    },
                });
                def.fail(ev.data.on_fail);
                this.dp.add(def).then(function (action) {
                // show effect if button have effect attribute
                // rainbowman can be displayed from two places: from attribute on a button or from python
                // code below handles the first case i.e 'effect' attribute on button.
                var effect = false;
                if (actionData.effect) {
                    effect = pyUtils.py_eval(actionData.effect);
                }

                if (action && action.constructor === Object) {
                    // filter out context keys that are specific to the current action, because:
                    //  - wrong default_* and search_default_* values won't give the expected result
                    //  - wrong group_by values will fail and forbid rendering of the destination view
                    var ctx = new Context(
                        _.object(_.reject(_.pairs(env.context), function (pair) {
                            return pair[0].match('^(?:(?:default_|search_default_|show_).+|' +
                                                 '.+_view_ref|group_by|group_by_no_leaf|active_id|' +
                                                 'active_ids)$') !== null;
                        }))
                    );
                    ctx.add(actionData.context || {});
                    ctx.add({active_model: env.model});
                    if (recordID) {
                        ctx.add({
                            active_id: recordID,
                            active_ids: [recordID],
                        });
                    }
                    ctx.add(action.context || {});
                    action.context = ctx;
                    // in case an effect is returned from python and there is already an effect
                    // attribute on the button, the priority is given to the button attribute
                    action.effect = effect || action.effect;
                } else {
                    // if action doesn't return anything, but there is an effect
                    // attribute on the button, display rainbowman
                    action = {
                        effect: effect,
                        type: 'ir.actions.act_window_close',
                    };
                }
                var options = {on_close: ev.data.on_closed};
                return self.doAction(action, options).then(ev.data.on_success, ev.data.on_fail);
                });

            } 
            else {
                return this._super.apply(this, arguments)
            };        
        },
    });


    ListController.include({
        _onSelectionChanged: function (event) {
            this._super.apply(this, arguments);
            var a = this.getSelectedIds();
        },
    });


    FormRenderer.include({
        custom_events: _.extend({}, FormRenderer.prototype.custom_events, {
            o2m_selection_changed: '_onSelectionChanged',
            o2m_create_selection_holder: '_createSelectionHolder'
        }),

        _createSelectionHolder: function(){
            this.o2mHolder = {};
        },

        _onSelectionChanged: function(event){

            var data = event.data;
            var fieldName = data['field_name'];
            this.o2mHolder[fieldName] = data.selection;
        }
    });
  


	var FieldOne2ManySelectable = FieldOne2Many.extend({
        custom_events: _.extend({}, FieldOne2Many.prototype.custom_events, {
            selection_changed: '_onSelectionChanged',
        }),

        init: function (parent, fieldName, options) {
            this._super.apply(this, arguments);
            this.parent = parent; // parent should be a form renderer
            this.fieldName = fieldName;
        },

        start: function(){
            this._super.apply(this, arguments);
            this.trigger_up('o2m_create_selection_holder', {});
        },

        _onSelectionChanged: function(_selection){
            // Notification will be sent to FormRender instance
            this.trigger_up('o2m_selection_changed', { selection: _selection, field_name: this.fieldName});
        },

        _render: function () {
            if (!this.view) {
                return this._super();
            }
            if (this.renderer) {
                this.currentColInvisibleFields = this._evalColumnInvisibleFields();
                this.renderer.updateState(this.value, {'columnInvisibleFields': this.currentColInvisibleFields});
                this.pager.updateState({ size: this.value.count });
                return $.when();
            }
            var arch = this.view.arch;
            var viewType;
            if (arch.tag === 'tree') {
                viewType = 'list';
                this.currentColInvisibleFields = this._evalColumnInvisibleFields();
                this.renderer = new ListRenderer(this, this.value, {
                    arch: arch,
                    editable: this.mode === 'edit' && arch.attrs.editable,
                    addCreateLine: !this.isReadonly && this.activeActions.create,
                    addTrashIcon: !this.isReadonly && this.activeActions.delete,
                    viewType: viewType,
                    columnInvisibleFields: this.currentColInvisibleFields,
                    hasSelectors: true,
                });
            }
            if (arch.tag === 'kanban') {
                viewType = 'kanban';
                var record_options = {
                    editable: false,
                    deletable: false,
                    read_only_mode: this.isReadonly,
                };
                this.renderer = new KanbanRenderer(this, this.value, {
                    arch: arch,
                    record_options: record_options,
                    viewType: viewType,
                });
            }
            this.$el.addClass('o_field_x2many o_field_x2many_' + viewType);
            return this.renderer ? this.renderer.appendTo(this.$el) : this._super();
        },
	});

	field_registry.add('one2many_checkbox', FieldOne2ManySelectable);

});


