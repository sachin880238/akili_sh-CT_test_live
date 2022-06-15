odoo.define('custom_addres_widget.custom', function (require) {
"use strict";
var AbstractField = require('web.AbstractField');
var core = require('web.core');
var fieldRegistry = require('web.field_registry');
var dialogs = require('web.view_dialogs');
var QWeb = core.qweb;
var FieldtextPreview = AbstractField.extend({
    className: 'd-block o_field_video_preview',
    events: {
             "click .search_icon": "on_search_icon",
             "click .edit_icon": "on_edit_icon",
             "click .delete_icon": "on_delete_icon",
         },
    _render: function () {
    	this.$el.html(QWeb.render('productVideo', {
            embedCode: this.value,
        }));
        if (this.mode ==="readonly"){
        	this.$el.find('.search_icon')[0].style.visibility = "hidden";
            this.$el.find('.edit_icon')[0].style.visibility = "hidden";
            this.$el.find('.delete_icon')[0].style.visibility = "hidden";
        }
        if(this.record.data.partner_contact_id){
            var self=this;
            this._rpc({
                model: 'sale.order',
                method: 'detail_contact_address',
                args: [this.record.data.partner_contact_id.res_id],
                context: this.context,
            }).then(function(arg) {
                var temp=self.$el[0].getElementsByClassName("text_data");
                temp[0].value=arg
                //console.log("------------------------------".self.record.context)
                if(self.record.context.params){
                if(self.record.context.params['contact_id'] !== undefined  ){
                self.record.context.params['contact_id']=''
            }
            // else{
            //     self.record.context.params['contact_id']=''
            // }

            if( self.record.context.params['billing_id'] !== undefined ){
                self.record.context.params['billing_id']=''
            }
            if( self.record.context.params['shipping_id'] !== undefined ){
                    self.record.context.params['shipping_id']=''
                }
            }
            // else{
            //     self.record.context.params['billing_id']=''
            // }


                // console.log("99999999999999999999999999999000000000000000000",self.$el[0],arg)
                // var temp=self.$el[0].getElementsByClassName("text_data");
                // console.log("99999999999999999999999999999000000000000000000",temp)
                // temp[0].value=arg

                             
                                            });


        }
        else{
                this.$el.find('.edit_icon')[0].style.visibility = "hidden";
                this.$el.find('.delete_icon')[0].style.visibility = "hidden";
             } 
    },
    on_search_icon: function(event){
        var dict={
    			0:['type_extend','=','contact']}
		var data=this.record.getContext(this.recordParams);
        var input_field= document.getElementsByClassName("partner_data");
        // var input = input_field[0].getElementsByTagName("INPUT")[0];
    	if (this.record.data.partner_id == false){
            if(input_field[0].value != ""){
                var self=this;
                    self._rpc({
                                        model: 'res.partner',
                                        method: 'name_search',
                                        kwargs: {
                                            name: '',
                                            args: [['parent_id','=', parseInt(input_field[0].value)],['type_extend','=','contact']],
                                            operator: "ilike",
                                            limit: 80,
                                            context: '',
                                        },
                                    }).then(
                                        self._searchCreatePopup.bind(self, "search")
                                        );
            console.log("=-=-ksldjkshkhhjdjhsdhsj")

        }
        }
        else{
            var self=this;
                    self._rpc({
                                        model: 'res.partner',
                                        method: 'name_search',
                                        kwargs: {
                                            name: '',
                                            args: [['parent_id','=',this.record.data.partner_id.data.id],['type_extend','=','contact']],
                                            operator: "ilike",
                                            limit: 80,
                                            context: '',
                                        },
                                    }).then(
                                        self._searchCreatePopup.bind(self, "search")
                                        );
        }
        
    	

			    	
                
    },
    _searchCreatePopup: function (view, ids, context,value=false) {
        var data=this.record.getContext(this.recordParams);
        var input_field= document.getElementsByClassName("partner_data");
    	var self = this;
        if (this.record.data.partner_id == false){
            if(input_field[0].value != ""){
                return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, {
            res_model: 'res.partner',
            domain: [['parent_id','=', parseInt(input_field[0].value)],['type_extend','=','contact']],
            context:{'address_view':true},
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: ids ? _.map(ids, function (x) { return x[0]; }) : undefined,
            initial_view: view,
            disable_multiple_selection: true,
            no_create: false,
            
            on_selected: function (records) {
                self.custom_set_values(records)
                // self.reinitialize(records[0]);
                // self.activate();
            }
        })).open();
        }
        }
        else{
            return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, {
            res_model: 'res.partner',
            domain: [['parent_id','=',this.record.data.partner_id.data.id],['type_extend','=','contact']],
            context:{'address_view':true},
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: ids ? _.map(ids, function (x) { return x[0]; }) : undefined,
            initial_view: view,
            disable_multiple_selection: true,
            no_create: false,
            
            on_selected: function (records) {
                console.log("---------------------==============",records)
                self.custom_set_values(records)
                // self.reinitialize(records[0]);
                // self.activate();
            }
        })).open();
        }
        
    },
    on_delete_icon: function(record){
        console.log("-----------------------",this.record.data.partner_contact_id)
        var self=this;
        if (this.record.data.partner_contact_id != false){
            console.log("---------------------sachin")
            if(confirm("Are you sure you want to delete?")){
            this._rpc({
                    model: 'sale.order',
                    method: 'delete_address_form',
                    args: [this.res_id, this.record.data.partner_contact_id.data.id],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    location.reload(true);
                    

                    

                                 
                                                });
            }


        }
        else{
            if(confirm("Are you sure you want to delete?")){
            console.log("skdsdhkshdshhdhshd")
            if(self.record.context.params['contact_id']  !== undefined ){
            self.record.context.params['contact_id']=''
            var temp=self.$el[0].getElementsByClassName("text_data");
                temp[0].value=''
                self.$el.find('.edit_icon')[0].style.visibility = "hidden";
                self.$el.find('.delete_icon')[0].style.visibility = "hidden";

            }
        }

        }
    },
    on_edit_icon: function(record){
        var self=this;
        console.log("------------------========",self.record.context.params['contact_id'])
        if (this.record.data.partner_id != false){
            if(this.record.data.partner_contact_id !=false){
                
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', self.record.data.partner_contact_id.data.id],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.data.partner_contact_id.data.id,
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new',
                        context:{'default_supplier': false, 'default_customer': false, 'default_street': false, 'default_street2': false, 'default_city': false, 'default_state_id': false, 'default_zip': false, 'default_country_id': false, 'default_address_view':true}
                      });

                    

                                 
                                                });




            }
            if(self.record.context.params['contact_id']){
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', self.record.context.params['contact_id']],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.context.params['contact_id'],
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new'
                      });

                    

                                 
                                                });

            }
            

        }
        else{
            var input_field= document.getElementsByClassName("partner_data");
            if(self.record.context.params['contact_id']){
                console.log("ggggggggggggggggggggggg")
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', parseInt(input_field[0].value)],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.context.params['contact_id'],
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new'
                      });

                    

                                 
                                                });


            }
        }
    },
    custom_set_values: function(record){
        var dataset = this.dataset;
        console.log("=======++++++++++++++++++++++++",dataset)
     //    var active_id = dataset.ids[dataset.index];
    	// console.log("-----------------------------",dataset,active_id)
        var self=this
        if (this.recordData.id){
            console.log("-=-djkfdhfhhddhfhd")
            this._rpc({
            model: 'sale.order',
            method: 'save_contact_address',
            args: [this.recordData.id, record[0]['id']],
            context: this.context,
        }).then(function(arg) {
            console.log("99999999999999999999999999999000000000000000000",self.$el[0],arg)
            var temp=self.$el[0].getElementsByClassName("text_data");
            console.log("99999999999999999999999999999000000000000000000",temp)
            temp[0].value=arg
            self.$el.find('.edit_icon')[0].style.visibility = "visible";
            self.$el.find('.delete_icon')[0].style.visibility = "visible";
            location.reload(true);

                         
                                        });
        }
        else{
            this._rpc({
            model: 'sale.order',
            method: 'save_contact_address',
            args: [this.recordData.id, record[0]['id']],
            context: this.context,
        }).then(function(arg) {
            console.log("99999999999999999999999999999000000000000000000",self)
            // self.recordData.partner_contact_id=parseInt(record[0]['id'])
            var temp=self.$el[0].getElementsByClassName("text_data");
            console.log("99999999999999999999999999999000000000000000000",temp)
            temp[0].value=arg
            console.log("---------------------------sachinkumar",self.record.context)
            self.record.context['invoice_id']={}
            self.record.context.params['contact_id']=record[0]['id']
            self.record.context['invoice_id']['data']=record[0]['id']
             // self.record.context.card_detail['data']=JSON.stringify(self.record.context);
            console.log("----------=-==-=-sdssssssssssssss",self)
            self.$el.find('.edit_icon')[0].style.visibility = "visible";
            self.$el.find('.delete_icon')[0].style.visibility = "visible";
            
            
            //self._super(record[0]['id']);
            
            // print("=ddddddddddddddddddddddddddddddddddd",self)


                         
                                        });

        }
        


    },
});
var billing_address = AbstractField.extend({
    className: 'd-block o_field_video_preview',
    events: {
             "click .search_icon": "on_search_icon",
             "click .edit_icon": "on_edit_icon",
             "click .delete_icon": "on_delete_icon",
         },
    _render: function () {
        this.$el.html(QWeb.render('billing_address', {
            embedCode: this.value,
        }));
        if (this.mode ==="readonly"){
            this.$el.find('.search_icon')[0].style.visibility = "hidden";
            this.$el.find('.edit_icon')[0].style.visibility = "hidden";
            this.$el.find('.delete_icon')[0].style.visibility = "hidden";
        }
        if(this.record.data.partner_invoice_id){
            var self=this;
            console.log("-----------------------------vvvvvvvvvv",this.record.data.partner_invoice_id.res_id)
            this._rpc({
                model: 'sale.order',
                method: 'detail_billing_address',
                args: [this.record.data.partner_invoice_id.res_id],
                context: this.context,
            }).then(function(arg) {
                console.log("=--sssssssssssssssssssssssdddddd",arg)
                var temp=self.$el[0].getElementsByClassName("billing_text_data");
                temp[0].value=arg
                if(self.record.context.params){
                if( self.record.context.params['contact_id']  !== undefined ){
                self.record.context.params['contact_id']=''
            }
            // else{
            //     self.record.context.params['contact_id']=''
            // }
                if( self.record.context.params['billing_id']  !== undefined ){
                self.record.context.params['billing_id']=''
            }
            if( self.record.context.params['shipping_id'] !== undefined ){
                    self.record.context.params['shipping_id']=''
                }
            }
            //     else{
            //     self.record.context.params['billing_id']=''
            // }


                // console.log("99999999999999999999999999999000000000000000000",self.$el[0],arg)
                // var temp=self.$el[0].getElementsByClassName("text_data");
                // console.log("99999999999999999999999999999000000000000000000",temp)
                // temp[0].value=arg

                             
                                            });


        } 
        else{
                this.$el.find('.edit_icon')[0].style.visibility = "hidden";
                this.$el.find('.delete_icon')[0].style.visibility = "hidden";
             } 
    },
    on_search_icon: function(event){
        var dict={
                0:['type_extend','=','contact']}
        var data=this.record.getContext(this.recordParams);
        var input_field= document.getElementsByClassName("partner_data");
        // var input = input_field[0].getElementsByTagName("INPUT")[0];
        if (this.record.data.partner_id == false){
            if(input_field[0].value != ""){
                var self=this;
                    self._rpc({
                                        model: 'res.partner',
                                        method: 'name_search',
                                        kwargs: {
                                            name: '',
                                            args: [['parent_id','=', parseInt(input_field[0].value)],['type_extend','=','invoice']],
                                            operator: "ilike",
                                            limit: 80,
                                            context: '',
                                        },
                                    }).then(
                                        self._searchCreatePopup.bind(self, "search")
                                        );
            console.log("=-=-ksldjkshkhhjdjhsdhsj")

        }
        }
        else{
            var self=this;
                    self._rpc({
                                        model: 'res.partner',
                                        method: 'name_search',
                                        kwargs: {
                                            name: '',
                                            args: [['parent_id','=',this.record.data.partner_id.data.id],['type_extend','=','invoice']],
                                            operator: "ilike",
                                            limit: 80,
                                            context: '',
                                        },
                                    }).then(
                                        self._searchCreatePopup.bind(self, "search")
                                        );
        }
        
        

                    
                
    },
    _searchCreatePopup: function (view, ids, context,value=false) {
        var data=this.record.getContext(this.recordParams);
        var input_field= document.getElementsByClassName("partner_data");
        var self = this;
        if (this.record.data.partner_id == false){
            if(input_field[0].value != ""){
                return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, {
            res_model: 'res.partner',
            domain: [['parent_id','=', parseInt(input_field[0].value)],['type_extend','=','invoice']],
            context:{'address_view':true},
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: ids ? _.map(ids, function (x) { return x[0]; }) : undefined,
            initial_view: view,
            disable_multiple_selection: true,
            no_create: false,
            
            on_selected: function (records) {
                self.custom_set_values(records)
                // self.reinitialize(records[0]);
                // self.activate();
            }
        })).open();
        }
        }
        else{
            return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, {
            res_model: 'res.partner',
            domain: [['parent_id','=',this.record.data.partner_id.data.id],['type_extend','=','invoice']],
            context:{'address_view':true},
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: ids ? _.map(ids, function (x) { return x[0]; }) : undefined,
            initial_view: view,
            disable_multiple_selection: true,
            no_create: false,
            
            on_selected: function (records) {
                console.log("---------------------==============",records)
                self.custom_set_values(records)
                // self.reinitialize(records[0]);
                // self.activate();
            }
        })).open();
        }
        
    },
    on_delete_icon: function(record){
        console.log("-----------------------",this.record.data.partner_contact_id)
        var self=this;
        if (this.record.data.partner_invoice_id != false){
            console.log("---------------------sachin")
            if(confirm("Are you sure you want to delete?")){
            this._rpc({
                    model: 'sale.order',
                    method: 'delete_billing_address_form',
                    args: [this.res_id, this.record.data.partner_invoice_id.data.id],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    location.reload(true);
                    

                    

                                 
                                                });
            }


        }
        else{
            if(confirm("Are you sure you want to delete?")){
            console.log("skdsdhkshdshhdhshd")
            if(self.record.context.params['billing_id']  !== undefined ){
            self.record.context.params['billing_id']=''
            var temp=self.$el[0].getElementsByClassName("billing_text_data");
                temp[0].value=''
                self.$el.find('.edit_icon')[0].style.visibility = "hidden";
                self.$el.find('.delete_icon')[0].style.visibility = "hidden";
            }
            else{
                var temp=self.$el[0].getElementsByClassName("billing_text_data");
                temp[0].value=''
                self.$el.find('.edit_icon')[0].style.visibility = "hidden";
                self.$el.find('.delete_icon')[0].style.visibility = "hidden";
            }
        }

        }
    },
    on_edit_icon: function(record){
        var self=this;
        console.log("------------------========",self.record.context.params['billing_id'])
        if (this.record.data.partner_id != false){
            if(this.record.data.partner_invoice_id !=false){
                
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', this.record.data.partner_id.data.id],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.data.partner_invoice_id.data.id,
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new'
                      });

                    

                                 
                                                });




            }
            if(self.record.context.params['billing_id']){
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', this.record.data.partner_id.data.id],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.context.params['billing_id'],
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new'
                      });

                    

                                 
                                                });

            }
            

        }
        else{
            var input_field= document.getElementsByClassName("partner_data");
            if(self.record.context.params['billing_id']){
                console.log("ggggggggggggggggggggggg")
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', parseInt(input_field[0].value)],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.context.params['billing_id'],
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new'
                      });

                    

                                 
                                                });


            }
        }
    },
    custom_set_values: function(record){
        var dataset = this.dataset;
        console.log("=======++++++++++++++++++++++++",dataset)
     //    var active_id = dataset.ids[dataset.index];
        // console.log("-----------------------------",dataset,active_id)
        var self=this
        if (this.recordData.id){
            console.log("-=-djkfdhfhhddhfhd")
            this._rpc({
            model: 'sale.order',
            method: 'save_billing_address',
            args: [this.recordData.id, record[0]['id']],
            context: this.context,
        }).then(function(arg) {
            console.log("=--sssssssssssssssssssssssdddddd",arg)
            console.log("99999999999999999999999999999000000000000000000",self.$el[0],arg)
            var temp=self.$el[0].getElementsByClassName("billing_text_data");
            console.log("99999999999999999999999999999000000000000000000",temp)
            temp[0].value=arg
            location.reload(true);

                         
                                        });
        }
        else{
            this._rpc({
            model: 'sale.order',
            method: 'save_billing_address',
            args: [this.recordData.id, record[0]['id']],
            context: this.context,
        }).then(function(arg) {
            console.log("=--sssssssssssssssssssssssdddddd",arg)
            console.log("99999999999999999999999999999000000000000000000",self)
            // self.recordData.partner_contact_id=parseInt(record[0]['id'])
            var temp=self.$el[0].getElementsByClassName("billing_text_data");
            console.log("99999999999999999999999999999000000000000000000",temp)
            temp[0].value=arg
            console.log("---------------------------sachinkumar",self.record.context)
            self.record.context['invoice_id']={}
            self.record.context.params['billing_id']=record[0]['id']
            self.record.context['invoice_id']['data']=record[0]['id']
             // self.record.context.card_detail['data']=JSON.stringify(self.record.context);
            console.log("----------=-==-=-sdssssssssssssss",self)
            self.$el.find('.edit_icon')[0].style.visibility = "visible";
            self.$el.find('.delete_icon')[0].style.visibility = "visible";
            
            //self._super(record[0]['id']);
            
            // print("=ddddddddddddddddddddddddddddddddddd",self)


                         
                                        });

        }
        


    },
});


var shipping_address = AbstractField.extend({
    className: 'd-block o_field_video_preview',
    events: {
             "click .search_icon": "on_search_icon",
             "click .edit_icon": "on_edit_icon",
             "click .delete_icon": "on_delete_icon",
         },
    _render: function () {
        this.$el.html(QWeb.render('shipping_address', {
            embedCode: this.value,
        }));
        if (this.mode ==="readonly"){
            this.$el.find('.search_icon')[0].style.visibility = "hidden";
            this.$el.find('.edit_icon')[0].style.visibility = "hidden";
            this.$el.find('.delete_icon')[0].style.visibility = "hidden";
        }
        if(this.record.data.partner_shipping_id){
            var self=this;
            console.log("-----------------------------vvvvvvvvvv",this.record.data.partner_invoice_id.res_id)
            this._rpc({
                model: 'sale.order',
                method: 'detail_shipping_address',
                args: [this.record.data.partner_shipping_id.res_id],
                context: this.context,
            }).then(function(arg) {
                console.log("=--sssssssssssssssssssssssdddddd",arg)
                var temp=self.$el[0].getElementsByClassName("shipping_text_data");
                temp[0].value=arg
                if(self.record.context.params){
                if( self.record.context.params['contact_id']  !== undefined ){
                    self.record.context.params['contact_id']=''
                }
                // else{
                //     self.record.context.params['contact_id']=''
                // }
                    if( self.record.context.params['billing_id']  !== undefined ){
                    self.record.context.params['billing_id']=''
                }
                //     else{
                //     self.record.context.params['billing_id']=''
                // }
                if( self.record.context.params['shipping_id']  !== undefined ){
                    self.record.context.params['shipping_id']=''
                }
            }
                //     else{
                //     self.record.context.params['shipping_id']=''
                // }


                // console.log("99999999999999999999999999999000000000000000000",self.$el[0],arg)
                // var temp=self.$el[0].getElementsByClassName("text_data");
                // console.log("99999999999999999999999999999000000000000000000",temp)
                // temp[0].value=arg

                             
                                            });


        } 
        else{
                this.$el.find('.edit_icon')[0].style.visibility = "hidden";
                this.$el.find('.delete_icon')[0].style.visibility = "hidden";
             } 
    },
    on_search_icon: function(event){
        var dict={
                0:['type_extend','=','contact']}
        var data=this.record.getContext(this.recordParams);
        var input_field= document.getElementsByClassName("partner_data");
        // var input = input_field[0].getElementsByTagName("INPUT")[0];
        if (this.record.data.partner_id == false){
            if(input_field[0].value != ""){
                var self=this;
                    self._rpc({
                                        model: 'res.partner',
                                        method: 'name_search',
                                        kwargs: {
                                            name: '',
                                            args: [['parent_id','=', parseInt(input_field[0].value)],['type_extend','=','delivery']],
                                            operator: "ilike",
                                            limit: 80,
                                            context: '',
                                        },
                                    }).then(
                                        self._searchCreatePopup.bind(self, "search")
                                        );
        }
        }
        else{
            var self=this;
                    self._rpc({
                                        model: 'res.partner',
                                        method: 'name_search',
                                        kwargs: {
                                            name: '',
                                            args: [['parent_id','=',this.record.data.partner_id.data.id],['type_extend','=','delivery']],
                                            operator: "ilike",
                                            limit: 80,
                                            context: '',
                                        },
                                    }).then(
                                        self._searchCreatePopup.bind(self, "search")
                                        );
        }
        
        

                    
                
    },
    _searchCreatePopup: function (view, ids, context,value=false) {
        var data=this.record.getContext(this.recordParams);
        var input_field= document.getElementsByClassName("partner_data");
        var self = this;
        if (this.record.data.partner_id == false){
            if(input_field[0].value != ""){
                return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, {
            res_model: 'res.partner',
            domain: [['parent_id','=', parseInt(input_field[0].value)],['type_extend','=','delivery']],
            context:{'address_view':true},
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: ids ? _.map(ids, function (x) { return x[0]; }) : undefined,
            initial_view: view,
            disable_multiple_selection: true,
            no_create: false,
            
            on_selected: function (records) {
                self.custom_set_values(records)
                // self.reinitialize(records[0]);
                // self.activate();
            }
        })).open();
        }
        }
        else{
            return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, {
            res_model: 'res.partner',
            domain: [['parent_id','=',this.record.data.partner_id.data.id],['type_extend','=','delivery']],
            context:{'address_view':true},
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: ids ? _.map(ids, function (x) { return x[0]; }) : undefined,
            initial_view: view,
            disable_multiple_selection: true,
            no_create: false,
            
            on_selected: function (records) {
                self.custom_set_values(records)
                // self.reinitialize(records[0]);
                // self.activate();
            }
        })).open();
        }
        
    },
    on_delete_icon: function(record){
        var self=this;
        if (this.record.data.partner_shipping_id != false){
            if(confirm("Are you sure you want to delete?")){
            this._rpc({
                    model: 'sale.order',
                    method: 'delete_shipping_address_form',
                    args: [this.res_id, this.record.data.partner_shipping_id.data.id],
                    context: this.context,
                }).then(function(arg) {
                    location.reload(true);
                    

                    

                                 
                                                });
            }


        }
        else{
            if(confirm("Are you sure you want to delete?")){
            if(self.record.context.params['shipping_id']){
            self.record.context.params['shipping_id']=''
            var temp=self.$el[0].getElementsByClassName("shipping_text_data");
                temp[0].value=''
                self.$el.find('.edit_icon')[0].style.visibility = "hidden";
                self.$el.find('.delete_icon')[0].style.visibility = "hidden";
            }
        }

        }
    },
    on_edit_icon: function(record){
        var self=this;
        if (this.record.data.partner_id != false){
            if(this.record.data.partner_shipping_id !=false){
                
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', this.record.data.partner_id.data.id],
                    context: this.context,
                }).then(function(arg) {
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.data.partner_shipping_id.data.id,
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new'
                      });

                    

                                 
                                                });




            }
            if(self.record.context.params['shipping_id']){
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', this.record.data.partner_id.data.id],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.context.params['shipping_id'],
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new'
                      });

                    

                                 
                                                });

            }
            

        }
        else{
            var input_field= document.getElementsByClassName("partner_data");
            if(self.record.context.params['shipping_id']){
                console.log("ggggggggggggggggggggggg")
                this._rpc({
                    model: 'sale.order',
                    method: 'get_contact_address_form',
                    args: ['sale.order', parseInt(input_field[0].value)],
                    context: this.context,
                }).then(function(arg) {
                    console.log("99999999999999999999999999999000000000000000000",arg)
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'res.partner',
                        res_id: self.record.context.params['shipping_id'],
                        view_mode: 'form',
                        views: [[arg, 'form']],
                        target: 'new'
                      });

                    

                                 
                                                });


            }
        }
    },
    custom_set_values: function(record){
        var dataset = this.dataset;
        console.log("=======++++++++++++++++++++++++",dataset)
     //    var active_id = dataset.ids[dataset.index];
        // console.log("-----------------------------",dataset,active_id)
        var self=this
        if (this.recordData.id){
            console.log("-=-djkfdhfhhddhfhd")
            this._rpc({
            model: 'sale.order',
            method: 'save_shipping_address',
            args: [this.recordData.id, record[0]['id']],
            context: this.context,
        }).then(function(arg) {
            console.log("=--sssssssssssssssssssssssdddddd",arg)
            console.log("99999999999999999999999999999000000000000000000",self.$el[0],arg)
            var temp=self.$el[0].getElementsByClassName("shipping_text_data");
            console.log("99999999999999999999999999999000000000000000000",temp)
            temp[0].value=arg
            location.reload(true);

                         
                                        });
        }
        else{
            this._rpc({
            model: 'sale.order',
            method: 'save_shipping_address',
            args: [this.recordData.id, record[0]['id']],
            context: this.context,
        }).then(function(arg) {
            console.log("=--sssssssssssssssssssssssdddddd",arg)
            console.log("99999999999999999999999999999000000000000000000",self)
            // self.recordData.partner_contact_id=parseInt(record[0]['id'])
            var temp=self.$el[0].getElementsByClassName("shipping_text_data");
            console.log("99999999999999999999999999999000000000000000000",temp)
            temp[0].value=arg
            console.log("---------------------------sachinkumar",self.record.context)
            self.record.context['invoice_id']={}
            self.record.context.params['shipping_id']=record[0]['id']
            self.record.context['invoice_id']['data']=record[0]['id']
             // self.record.context.card_detail['data']=JSON.stringify(self.record.context);
            console.log("----------=-==-=-sdssssssssssssss",self)
            self.$el.find('.edit_icon')[0].style.visibility = "visible";
            self.$el.find('.delete_icon')[0].style.visibility = "visible";
            
            //self._super(record[0]['id']);
            
            // print("=ddddddddddddddddddddddddddddddddddd",self)


                         
                                        });

        }
        


    },
});
fieldRegistry.add('customwidget', FieldtextPreview);
fieldRegistry.add('customwidgetbilling', billing_address);
fieldRegistry.add('customwidgetshipping', shipping_address);
return {'FieldtextPreview':FieldtextPreview,
        'billing_address':billing_address,
        'shipping_address':shipping_address};

// screens.define_action_button({
//     'name': 'chatter_button',
//     'widget': CommentButton,
// });



});
