odoo.define('shipment.PickingBarcodeHandler', function (require) {
"use strict";

var core = require('web.core');
var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');
var FormController = require('web.FormController');

var _t = core._t;

FormController.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Override to take into account 'location_processed' and 'result_package_id'
     * to determine whether or not the given barcode matches the given record in
     * the case of a 'picking_barcode_handler' widget.
     *
     * @private
     * @override
     * @param {Object} record
     * @param {string} barcode
     * @param {Object} activeBarcode
     * @returns {boolean}
     */
    _barcodeRecordFilter: function (record, barcode) { 
        var tablist = $('.nav-tabs .active').text()
        var self = this;
        var res_id = false
        var url_dict = {}
        url_dict['tag'] = tablist
        url_dict['tag'] = tablist
 
    },

    _barcodePickingAddRecordId: function (barcode, activeBarcode) {  
        console.log(this.mode)
        var tablist = $('.nav-tabs .active').text()
        var check_wiz = document.getElementsByClassName("modal-content")
        console.log(check_wiz)
        if (!check_wiz){
            console.log()
        }
        
        console.log(tablist)
        var self = this;
        var res_id = false
        var url_dict = {}
        var fetch_ur_str = window.location.href.toString()
        var fetch_url = fetch_ur_str.split('#')[1].split('&')
        var picking_id = fetch_ur_str.split('id=')[1].split('&')
        console.log(picking_id[0])
        url_dict[fetch_url[0].split('=')[0]] = fetch_url[0].split('=')[1]
        url_dict['tag'] = tablist
        url_dict['barcode'] = barcode
        url_dict['wizard'] = check_wiz
        url_dict['picking_id']=picking_id[0]
        this._rpc({
            model: 'stock.picking',
            method: 'on_barcode_scanned1',
            args:[url_dict]
        })

        .then(function(res) {
            if(tablist === "PRODUCTS"){
                res_id = res.res_id
                if (res_id){
                console.log(typeof res_id[6],typeof parseFloat(res_id[6])) 
                    self.do_action({
                        name:"Wizard:Product Action",  
                        type: 'ir.actions.act_window',
                        res_model: 'stock.move',
                        view_mode: 'form',
                        view_type: 'form',
                        // record_id: active_id,
                        // view_id: res.view_id,
                        res_id: res_id[0],
                        views: [[res.view_id, 'form']],
                        target: 'new',
                        context:{}
                            });
                } 
                else{
                    alert("move product not found")
                }
            }

            

        }); 


        if (!activeBarcode.handle) {
            return Promise.reject();
        }
        var record = this.model.get(activeBarcode.handle);
        if (record.data.state === 'cancel' || record.data.state === 'done') {
            this.do_warn(_.str.sprintf(_t("Picking %s"), record.data.state),
                _.str.sprintf(_t("The picking is %s and cannot be edited."), record.data.state));
            return Promise.reject();
        }
        return this._barcodeAddX2MQuantity(barcode, activeBarcode);
    }
});


var PickingBarcodeHandler = AbstractField.extend({
    init: function() {
        console.log()
        this._super.apply(this, arguments);

        this.trigger_up('activeBarcode', {
            name: this.name,
            notifyChange: false,
            fieldName: 'move_ids_without_package',
            quantity: 'qty_done',
            setQuantityWithKeypress: true,
            commands: {
                'barcode': '_barcodePickingAddRecordId',
                'O-CMD.MAIN-MENU': _.bind(this.do_action, this, 'shipment.stock_barcode_action_main_menu', {clear_breadcrumbs: true}),
            }
        });
    },
});

field_registry.add('picking_barcode_handler', PickingBarcodeHandler);

return PickingBarcodeHandler;

});
