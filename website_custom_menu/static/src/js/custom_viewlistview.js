odoo.define('website_custom_menu.custom_viewlistview', function (require) {
"use strict";

/**
 * The list view is one of the core and most basic view: it is used to look at
 * a list of records in a table.
 *
 * Note that a list view is not instantiated to display a one2many field in a
 * form view. Only a ListRenderer is used in that case.
 */

var BasicView = require('web.BasicView');
var core = require('web.core');
var ListView=require('web.ListView')
var ListRenderer = require('web.ListRenderer');
var ListController = require('web.ListController');

var _lt = core._lt;

ListView.include({
    
    init: function (viewInfo, params) {
        if(params.action){
        params.action_id=params.action.id
    }
        this._super.apply(this, arguments);
        if(params.action){
        this.rendererParams.action_id=params.action.id
        }
        var selectedRecords = []; // there is no selected records by default

        var mode = this.arch.attrs.editable && !params.readonly ? "edit" : "readonly";
        
        this.controllerParams.editable = this.arch.attrs.editable;
        this.controllerParams.hasSidebar = params.hasSidebar;
        this.controllerParams.toolbarActions = viewInfo.toolbar;
        this.controllerParams.noLeaf = !!this.loadParams.context.group_by_no_leaf;
        this.controllerParams.mode = mode;
        this.controllerParams.selectedRecords = selectedRecords;

        this.rendererParams.arch = this.arch;
        this.rendererParams.hasSelectors =
                'hasSelectors' in params ? params.hasSelectors : true;
        this.rendererParams.editable = params.readonly ? false : this.arch.attrs.editable;
        this.rendererParams.selectedRecords = selectedRecords;

        this.loadParams.limit = this.loadParams.limit || 80;
        this.loadParams.type = 'list';
    },
});



});
