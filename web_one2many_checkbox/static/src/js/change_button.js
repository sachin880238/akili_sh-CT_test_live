odoo.define('web_one2many_checkbox.change_button', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var data = require('web.data');
var viewDialogs = require('web.view_dialogs');
var _t = core._t;


/**
 * Create and edit dialog (displays a form view record and leave once saved)
 */
var FormViewDialog = ViewDialog.extend({
    
    init: function (options) {
        var self = this;
        options = options || {};

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
                text: (readonly ? _t("Close") : _t("CANCEL")),
                classes: "btn-secondary o_form_button_cancel",
                close: true,
                click: function () {
                    if (!readonly) {
                        self.form_view.model.discardChanges(self.form_view.handle, {
                            rollback: self.shouldSaveLocally,
                        });
                    }
                },
            }];

            if (!readonly) {
                options.buttons.unshift({
                    text: (multi_select ? _t("SAVE") : _t("Save")),
                    classes: "btn-primary",
                    click: function () {
                        this._save().then(self.close.bind(self));
                    }
                });

                if (multi_select) {
                    options.buttons.splice(1, 0, {
                        text: _t("NEW"),
                        classes: "btn-primary",
                        click: function () {
                            this._save().then(self.form_view.createRecord.bind(self.form_view, self.parentID));
                        },
                    });
                }

                // var multi = options.disable_multiple_selection;
                // if (!multi && this.deletable) {
                //     options.buttons.push({
                //         text: _t("Remove"),
                //         classes: 'btn-secondary o_btn_remove',
                //         click: this._remove.bind(this),
                //     });
                // }
            }
        }
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    });

return {
    FormViewDialog: FormViewDialog,
};

});
