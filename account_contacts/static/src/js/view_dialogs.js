odoo.define('web.view_dialogs', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var dom = require('web.dom');
var ListController = require('web.ListController');
var ListView = require('web.ListView');
var pyUtils = require('web.py_utils');
var SearchView = require('web.SearchView');
var view_registry = require('web.view_registry');

var _t = core._t;

/**
 * Class with everything which is common between FormViewDialog and
 * SelectCreateDialog.
 */
var ViewDialog = Dialog.extend({
    custom_events: _.extend({}, Dialog.prototype.custom_events, {
        push_state: '_onPushState',
        env_updated: function (event) {
            event.stopPropagation();
        },
    }),
    /**
     * @constructor
     * @param {Widget} parent
     * @param {options} [options]
     * @param {string} [options.dialogClass=o_act_window]
     * @param {string} [options.res_model] the model of the record(s) to open
     * @param {any[]} [options.domain]
     * @param {Object} [options.context]
     */
    init: function (parent, options) {
        options = options || {};
        options.fullscreen = config.device.isMobile;
        options.dialogClass = options.dialogClass || '' + ' o_act_window';
        console.log("7777777777777777777777777--------------------->>>",options.field_name)

        this._super(parent, $.extend(true, {}, options));
        this.res_model = options.res_model || null;
        this.domain = options.domain || [];
        this.fields_name=options.field_name || '';
        this.context = options.context || {};
        this.options = _.extend(this.options || {}, options || {});

        // FIXME: remove this once a dataset won't be necessary anymore to interact
        // with data_manager and instantiate views
        this.dataset = new data.DataSet(this, this.res_model, this.context);
        
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * We stop all push_state events from bubbling up.  It would be weird to
     * change the url because a dialog opened.
     *
     * @param {OdooEvent} event
     */
    _onPushState: function (event) {
        event.stopPropagation();
    },
});

/**
 * Create and edit dialog (displays a form view record and leave once saved)
 */
var FormViewDialog = ViewDialog.extend({
    /**
     * @param {Widget} parent
     * @param {Object} [options]
     * @param {string} [options.parentID] the id of the parent record. It is
     *   useful for situations such as a one2many opened in a form view dialog.
     *   In that case, we want to be able to properly evaluate domains with the
     *   'parent' key.
     * @param {integer} [options.res_id] the id of the record to open
     * @param {Object} [options.form_view_options] dict of options to pass to
     *   the Form View @todo: make it work
     * @param {Object} [options.fields_view] optional form fields_view
     * @param {boolean} [options.readonly=false] only applicable when not in
     *   creation mode
     * @param {boolean} [options.deletable=false] whether or not the record can
     *   be deleted
     * @param {boolean} [options.disable_multiple_selection=false] set to true
     *   to remove the possibility to create several records in a row
     * @param {function} [options.on_saved] callback executed after saving a
     *   record.  It will be called with the record data, and a boolean which
     *   indicates if something was changed
     * @param {function} [options.on_remove] callback executed when the user
     *   clicks on the 'Remove' button
     * @param {BasicModel} [options.model] if given, it will be used instead of
     *  a new form view model
     * @param {string} [options.recordID] if given, the model has to be given as
     *   well, and in that case, it will be used without loading anything.
     * @param {boolean} [options.shouldSaveLocally] if true, the view dialog
     *   will save locally instead of actually saving (useful for one2manys)
     */
    init: function (parent, options) {
        var self = this;
        options = options || {};

        this.help = false;
        this.res_id = options.res_id || null;
        this.on_saved = options.on_saved || (function () {});
        this.on_remove = options.on_remove || (function () {});
        this.context = options.context;
        this.model = options.model;
        this.parentID = options.parentID;
        this.recordID = options.recordID;
        this.shouldSaveLocally = options.shouldSaveLocally;
        this.readonly = options.readonly;
        this.deletable = options.deletable;
        this.disable_multiple_selection = options.disable_multiple_selection;

        var multi_select = !_.isNumber(options.res_id) && !options.disable_multiple_selection;
        var readonly = _.isNumber(options.res_id) && options.readonly;

        if (!options.buttons) {
            options.buttons = [{
                text: (readonly ? _t("CLOSE") : _t("CANCEL")),
                classes: (readonly ? ("btn-primary o_form_button_cancel") : ("btn-secondary o_form_button_cancel")),
                close: true,
                click: function () {
                    this.help = false;
                    if (!readonly) {
                        self.form_view.model.discardChanges(self.form_view.handle, {
                            rollback: self.shouldSaveLocally,
                        });
                    }
                },
            }];

            options.buttons.push({
                text: _t(""),
                classes: 'btn-light fa fa-question',
                click: this.on_click,
            });

            if (!readonly) {
                options.buttons.unshift({
                    text: (multi_select ? _t("SAVE") : _t("SAVE")),
                    classes: "btn-primary",
                    click: function () {
                        this.help = false;
                        this._save().then(self.close.bind(self));
                    }
                });

                if (multi_select) {
                    options.buttons.splice(1, 0, {
                        text: _t("NEW"),
                        classes: "btn-secondary",
                        click: function () {
                            this.help = false;
                            this._save().then(self.form_view.createRecord.bind(self.form_view, self.parentID));
                        },
                    });
                }

                var multi = options.disable_multiple_selection;
                if (!multi && this.deletable) {
                    options.buttons.push({
                        text: _t("REMOVE"),
                        classes: 'btn-secondary o_btn_remove',
                        click: this._remove.bind(this),
                    });
                }
            }
        }
        this._super(parent, options);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Open the form view dialog.  It is necessarily asynchronous, but this
     * method returns immediately.
     *
     * @returns {FormViewDialog} this instance
     */
    open: function () {
        var self = this;
        var specific_record = ['partner_shipping_id', 'partner_invoice_id', 'partner_contact_id'];
        console.log("ddddddddddddddddddddddddddddsdsds---------------------->>>>>>>>>>>>>>>",this,specific_record.includes(this.fields_name),this.res_model)
        var _super = this._super.bind(this);
        // if(specific_record.includes(this.fields_name) && this.res_model == "res.partner"){
        //     console.log("fffffffffffffffffffgfgfgffffg")
        //     self._rpc({
        //     model: 'res.partner',
        //     method: 'custom_get_view_id',
        //     args:[]
        // }).then(function (action) {
        //     console.log("------------------------------------------------")
        //         self.options['view_id']=action
        
        // var FormView = view_registry.get('form');
        // console.log("ffffffffffffgfgfgfgfgfgfffgffg222222222222222222",FormView)
        // var fields_view_def;
        // console.log("ddddddddddddddddddddddddddddsdsds",self.options.view_id)
        // if (self.options.fields_view) {
        //     fields_view_def = $.when(self.options.fields_view);
        // } else {
        //     console.log("========================------------",self.dataset, self.options.view_id)
        //     fields_view_def = self.loadFieldView(self.dataset, self.options.view_id, 'form');
        // }
        // console.log("dddddddddddddfdfddf555555555555",fields_view_def)

        // fields_view_def.then(function (viewInfo) {
        //     console.log("55555555555555555555555555",viewInfo)
        //     var refinedContext = _.pick(self.context, function (value, key) {
        //         return key.indexOf('_view_ref') === -1;
        //     });
        //     console.log("dddddddddddddddddddfffffffffffff",refinedContext)
        //     var formview = new FormView(viewInfo, {
        //         modelName: self.res_model,
        //         context: refinedContext,
        //         ids: self.res_id ? [self.res_id] : [],
        //         currentId: self.res_id || undefined,
        //         index: 0,
        //         mode: self.res_id && self.options.readonly ? 'readonly' : 'edit',
        //         footerToButtons: true,
        //         default_buttons: false,
        //         withControlPanel: false,
        //         model: self.model,
        //         parentID: self.parentID,
        //         recordID: self.recordID,
        //     });
        //     console.log("67767676767677677777777777777777766666666666666666",self)
        //     return formview.getController(self);
        // }).then(function (formView) {
        //     self.form_view = formView;
        //     var fragment = document.createDocumentFragment();
        //     if (self.recordID && self.shouldSaveLocally) {
        //         self.model.save(self.recordID, {savePoint: true});
        //     }
        //     console.log("7777777777777777tttttttttttttttttt",self.form_view)
        //     self.form_view.appendTo(fragment)
        //         .then(function () {
        //             self.opened().always(function () {
        //                 var $buttons = $('<div>');
        //                 self.form_view.renderButtons($buttons);
        //                 if ($buttons.children().length) {
        //                     self.$footer.empty().append($buttons.contents());
        //                 }
        //                 dom.append(self.$el, fragment, {
        //                     callbacks: [{widget: self.form_view}],
        //                     in_DOM: true,
        //                 });
        //             });
        //             _super();
        //         });
        // });

        // return self;
        //     });
            
       
        // this.options['view_id']=2205
        
        var FormView = view_registry.get('form');
        console.log("ffffffffffffgfgfgfgfgfgfffgffg----------------------------------------",FormView)
        var fields_view_def;
        console.log("ddddddddddddddddddddddddddddsdsds",this.options.view_id)
        if (this.options.fields_view) {
            fields_view_def = $.when(this.options.fields_view);
        } else {
            fields_view_def = this.loadFieldView(this.dataset, this.options.view_id, 'form');
        }

        fields_view_def.then(function (viewInfo) {
            var refinedContext = _.pick(self.context, function (value, key) {
                return key.indexOf('_view_ref') === -1;
            });
            var formview = new FormView(viewInfo, {
                modelName: self.res_model,
                context: refinedContext,
                ids: self.res_id ? [self.res_id] : [],
                currentId: self.res_id || undefined,
                index: 0,
                mode: self.res_id && self.options.readonly ? 'readonly' : 'edit',
                footerToButtons: true,
                default_buttons: false,
                withControlPanel: false,
                model: self.model,
                parentID: self.parentID,
                recordID: self.recordID,
            });
            return formview.getController(self);
        }).then(function (formView) {
            self.form_view = formView;
            var fragment = document.createDocumentFragment();
            if (self.recordID && self.shouldSaveLocally) {
                self.model.save(self.recordID, {savePoint: true});
            }
            self.form_view.appendTo(fragment)
                .then(function () {
                    self.opened().always(function () {
                        var $buttons = $('<div>');
                        self.form_view.renderButtons($buttons);
                        if ($buttons.children().length) {
                            self.$footer.empty().append($buttons.contents());
                        }
                        dom.append(self.$el, fragment, {
                            callbacks: [{widget: self.form_view}],
                            in_DOM: true,
                        });
                    });
                    _super();
                });
        });

        return this;
    
    return this;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _focusOnClose: function() {
        var isFocusSet = false;
        this.trigger_up('form_dialog_discarded', {
            callback: function (isFocused) {
                isFocusSet = isFocused;
            },
        });
        return isFocusSet;
    },

    /**
     * @private
     */
    _remove: function () {
        this.help = false;
        this.on_remove();
        this.close();
    },

    on_click: function () {
        document.getElementById(this.$modal[0].id).style.display = 'none';
        var url_dict = {'res_model': this['res_model'], 'title': this['title'], 'view_type': "form"}
        var parent_dict = {}
        var fetch_url = window.location.href.split('#')[1].split('&')
        for(var val in fetch_url) {
            if (fetch_url[val].split('=')[0] == 'model' || fetch_url[val].split('=')[0] == 'view_type'){
                parent_dict[fetch_url[val].split('=')[0]] = fetch_url[val].split('=')[1]
            }else{
                parent_dict[fetch_url[val].split('=')[0]] = parseInt(fetch_url[val].split('=')[1])
            }
        }

        var res_id = false
        var action_name = false
        var self = this;
        this.help = true;
       
        this._rpc({
            model: 'erp.help',
            method: 'fetch_child_rec_help',
            args:[url_dict, parent_dict]
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
                        'default_description':'<h3 style="text-align: center;"><b><font style="background-color: rgb(247, 247, 247); color: rgb(255, 0, 0); font-size: 36px;"></font></b></h3>'}
                });

            }else{ 
                if(res_id){
                    self.do_action({
                        name:"Help",  
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
                        name:"Help",  
                        type: 'ir.actions.act_window',
                        res_model: 'erp.help.wizard',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        context:{'url_dict':url_dict,'default_description':'<h3 style="text-align: center;"><b><font style="background-color: rgb(247, 247, 247); color: rgb(0, 209, 156); font-size: 36px;"></font></b></h3>'}
                    });
                }
            }
            
        });
    },

    /**
     * @private
     * @returns {Deferred}
     */
    _save: function () {
        var self = this;
        return this.form_view.saveRecord(this.form_view.handle, {
            stayInEdit: true,
            reload: false,
            savePoint: this.shouldSaveLocally,
            viewType: 'form',
        }).then(function (changedFields) {
            // record might have been changed by the save (e.g. if this was a new record, it has an
            // id now), so don't re-use the copy obtained before the save
            var record = self.form_view.model.get(self.form_view.handle);
            self.on_saved(record, !!changedFields.length);
        });
    },
});

var SelectCreateListController = ListController.extend({
    // Override the ListView to handle the custom events 'open_record' (triggered when clicking on a
    // row of the list) such that it triggers up 'select_record' with its res_id.
    custom_events: _.extend({}, ListController.prototype.custom_events, {
        open_record: function (event) {
            var selectedRecord = this.model.get(event.data.id);
            this.trigger_up('select_record', {
                id: selectedRecord.res_id,
                display_name: selectedRecord.data.display_name,
            });
        },
    }),
});

/**
 * Search dialog (displays a list of records and permits to create a new one by switching to a form view)
 */
var SelectCreateDialog = ViewDialog.extend({
    custom_events: _.extend({}, ViewDialog.prototype.custom_events, {
        select_record: function (event) {
            if (!this.options.readonly) {
                this.on_selected([event.data]);
                this.close();
            }
        },
        selection_changed: function (event) {
            event.stopPropagation();
            this.$footer.find(".o_select_button").prop('disabled', !event.data.selection.length);
        },
        search: function (event) {
            event.stopPropagation(); // prevent this event from bubbling up to the action manager
            var d = event.data;
            var searchData = this._process_search_data(d.domains, d.contexts, d.groupbys);
            this.list_controller.reload(_.extend({offset: 0}, searchData));
        },
        get_controller_context: '_onGetControllerContext',
    }),

    /**
     * options:
     * - initial_ids
     * - initial_view: form or search (default search)
     * - list_view_options: dict of options to pass to the List View
     * - on_selected: optional callback to execute when records are selected
     * - disable_multiple_selection: true to allow create/select multiple records
     */
    init: function () {
        this._super.apply(this, arguments);
        _.defaults(this.options, { initial_view: 'search' });
        this.on_selected = this.options.on_selected || (function () {});
        this.initial_ids = this.options.initial_ids;
    },

    open: function () {
        if (this.options.initial_view !== "search") {
            return this.create_edit_record();
        }
        var self = this;
        var user_context = this.getSession().user_context;

        var _super = this._super.bind(this);
        var context = pyUtils.eval_domains_and_contexts({
            domains: [],
            contexts: [user_context, this.context]
        }).context;
        var search_defaults = {};
        _.each(context, function (value_, key) {
            var match = /^search_default_(.*)$/.exec(key);
            if (match) {
                search_defaults[match[1]] = value_;
            }
        });
        this.loadViews(this.dataset.model, this.dataset.get_context().eval(), [[false, 'list'], [false, 'search']], {})
            .then(this.setup.bind(this, search_defaults))
            .then(function (fragment) {
                self.opened().then(function () {
                    dom.append(self.$el, fragment, {
                        callbacks: [{widget: self.list_controller}],
                        in_DOM: true,
                    });
                    self.set_buttons(self.__buttons);
                });
                _super();
            });
        return this;
    },

    setup: function (search_defaults, fields_views) {
        var self = this;
        var fragment = document.createDocumentFragment();

        var searchDef = $.Deferred();

        // Set the dialog's header and its search view
        var $header = $('<div/>').addClass('o_modal_header').appendTo(fragment);
        var $pager = $('<div/>').addClass('o_pager').appendTo($header);
        var options = {
            $buttons: $('<div/>').addClass('o_search_options').appendTo($header),
            search_defaults: search_defaults,
        };
        var searchview = new SearchView(this, this.dataset, fields_views.search, options);
        searchview.prependTo($header).done(function () {
            var d = searchview.build_search_data();
            if (self.initial_ids) {
                d.domains.push([["id", "in", self.initial_ids]]);
                self.initial_ids = undefined;
            }
            var searchData = self._process_search_data(d.domains, d.contexts, d.groupbys);
            searchDef.resolve(searchData);
        });

        return $.when(searchDef).then(function (searchResult) {
            // Set the list view
            var listView = new ListView(fields_views.list, _.extend({
                context: searchResult.context,
                domain: searchResult.domain,
                groupBy: searchResult.groupBy,
                modelName: self.dataset.model,
                hasSelectors: !self.options.disable_multiple_selection,
                readonly: true,
            }, self.options.list_view_options));
            listView.setController(SelectCreateListController);
            return listView.getController(self);
        }).then(function (controller) {
            self.list_controller = controller;
            // Set the dialog's buttons
            self.__buttons = [{
                text: _t("Cancel"),
                classes: "btn-secondary o_form_button_cancel",
                close: true,
            }];
            if (!self.options.no_create) {
                self.__buttons.unshift({
                    text: _t("Create"),
                    classes: "btn-primary",
                    click: self.create_edit_record.bind(self)
                });
            }
            if (!self.options.disable_multiple_selection) {
                self.__buttons.unshift({
                    text: _t("Select"),
                    classes: "btn-primary o_select_button",
                    disabled: true,
                    close: true,
                    click: function () {
                        var records = self.list_controller.getSelectedRecords();
                        var values = _.map(records, function (record) {
                            return {
                                id: record.res_id,
                                display_name: record.data.display_name,
                            };
                        });
                        self.on_selected(values);
                    },
                });
            }
            return self.list_controller.appendTo(fragment);
        }).then(function () {
            searchview.toggle_visibility(true);
            self.list_controller.do_show();
            self.list_controller.renderPager($pager);
            return fragment;
        });
    },
    _process_search_data: function (domains, contexts, groupbys) {
        var results = pyUtils.eval_domains_and_contexts({
            domains: [this.domain].concat(domains),
            contexts: [this.context].concat(contexts),
            group_by_seq: groupbys || [],
            eval_context: this.getSession().user_context,
        });
        var context = _.omit(results.context, function (value, key) { return key.indexOf('search_default_') === 0; });
        return {
            context: context,
            domain: results.domain,
            groupBy: results.group_by,
        };
    },
    create_edit_record: function () {
        var self = this;
        var dialog = new FormViewDialog(this, _.extend({}, this.options, {
            on_saved: function (record) {
                var values = [{
                    id: record.res_id,
                    display_name: record.data.display_name || record.data.name,
                }];
                self.on_selected(values);
            },
        })).open();
        dialog.on('closed', this, this.close);
        return dialog;
    },
    /**
     * @override
     */
    _focusOnClose: function() {
        var isFocusSet = false;
        this.trigger_up('form_dialog_discarded', {
            callback: function (isFocused) {
                isFocusSet = isFocused;
            },
        });
        return isFocusSet;
    },
    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Handles a context request: provides to the caller the context of the
     * list controller.
     *
     * @private
     * @param {OdooEvent} ev
     * @param {function} ev.data.callback used to send the requested context
     */
    _onGetControllerContext: function (ev) {
        ev.stopPropagation();
        var context = this.list_controller && this.list_controller.getContext();
        ev.data.callback(context || {});
    }
});

return {
    FormViewDialog: FormViewDialog,
    SelectCreateDialog: SelectCreateDialog,
};

});
