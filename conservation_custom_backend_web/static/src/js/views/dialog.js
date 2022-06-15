odoo.define('system_app.Dialog', function (require) {
"use strict";

var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;

var config = require('web.config');

var data = require('web.data');

var dom = require('web.dom');
var ListController = require('web.ListController');
var ListView = require('web.ListView');
var pyUtils = require('web.py_utils');
var SearchView = require('web.SearchView');
var view_registry = require('web.view_registry');

var _t = core._t;


var HelpDialogue = Dialog.extend({
    template: "HelpWizard",
    init: function (parent, name, value) {
        var self=this
        this.name = name;
        this.value = value;
        var modal=this._super(parent, {
            title: _.str.sprintf(_t("Help")),
            size: value,
            buttons: [
            {
                text: _t('Close'),
                classes: 'btn-primary close_button',
                close: true,
            },
            {
                text: _t('Edit'),
                classes: 'btn btn-secondary edit_button',
                click: function () {
                    this.$footer[0].childNodes[2].classList.remove("d-none");
                    this.$footer[0].childNodes[3].classList.remove("d-none");
                    this.$footer[0].childNodes[1].classList.add("d-none");
                    this.$footer[0].childNodes[0].classList.add("d-none");
                    this.$el[8].style.display="block"
                    this.$el[6].style.display="none"
                    var heading =this.$el[4].getElementsByClassName('main_heading')
                    heading[0].style.display="none"
                    var input_heading = this.$el[4].getElementsByClassName('heading_input')
                    input_heading[0].style.display="block"
                    // this.$el[6].style.setAttribute("display", "block");
                },
            },
                {
                text: _t('Save'),
                classes: 'btn-primary save_button d-none',
                click: function () {
                    var self=this;
                    var editor = tinymce.get('mytextarea'); // use your own editor id here - equals the id of your textarea
                    var content = editor.getContent();
                    var input_heading = self.$el[4].getElementsByClassName('heading_input')
                    var data_dict={'id':self.$el[10].innerHTML,'desc':content,'input':input_heading[0].value}
                    this._rpc({
                        model: 'erp.help',
                        method: 'save_data',
                        args:[data_dict]
                    })
                    .then(function(res) {
                        
                    var editor = tinymce.get('mytextarea'); // use your own editor id here - equals the id of your textarea
                    var content = editor.getContent();
                    self.$footer[0].childNodes[2].classList.add("d-none");
                    self.$footer[0].childNodes[1].classList.remove("d-none");
                    self.$footer[0].childNodes[3].classList.add("d-none");
                    self.$footer[0].childNodes[0].classList.remove("d-none");
                    self.$el[8].style.display="none"
                    self.$el[6].style.display="block"
                    self.$el[6].innerHTML=content
                    var heading =self.$el[4].getElementsByClassName('main_heading')
                    heading[0].style.display="block"
                    var input_heading = self.$el[4].getElementsByClassName('heading_input')
                    input_heading[0].style.display="none"
                    heading[0].innerHTML=input_heading[0].value
                    });
                    
                    
                },
            },
            {
                text: _t('Cancel'),
                classes: 'btn-secondary cancel_button d-none',
                close: true,
            },],
        });
        
        

  

    },
    start: function () {
        
    },
    /**
     * @override
     * @param {boolean} isSet
     */
    close: function (isSet) {
        this.isSet = isSet;
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    destroy: function () {
        if (!this.isSet) {
            this.trigger_up('closed_unset');
        }
        this._super.apply(this, arguments);
    },
});

Dialog.include({
    xmlDependencies: ['/conservation_custom_backend_web/static/src/xml/custom_dialog.xml'],

    willStart: function () {
        var query = false;
        var self = this;
        if (self.title === 'Help') {
            self.query = true;
        }
        else{
            if(self.buttons.length == 0){
                self.buttons.push({
                    text: _t(""),
                    classes: 'btn-light custom_button fa fa-question',
                    click: self.on_click,
            });
        }
        }
        return this._super.apply(this, arguments).then(function () {
            // Render modal once xml dependencies are loaded
            self.$modal = $(QWeb.render('Dialog', {
                fullscreen: self.fullscreen,
                title: self.title,
                subtitle: self.subtitle,
                technical: self.technical,
                query: self.query,
            }));
            var content = document.getElementsByClassName('modal o_technical_modal show')[0]
            if (content)
            {
                document.getElementsByClassName('modal o_technical_modal show')[0].style.display = 'none';
            }
            switch (self.size) {
                case 'large':
                    self.$modal.find('.modal-dialog').addClass('modal-lg');
                    break;
                case 'small':
                    self.$modal.find('.modal-dialog').addClass('modal-sm');
                    break;
            }
            self.$footer = self.$modal.find(".modal-footer");
            self.set_buttons(self.buttons);
            self.$modal.on('hidden.bs.modal', _.bind(self.destroy, self));
        });
    },
    on_click: function () {
        document.getElementById(this.$modal[0].id).style.display = 'none';
        var url_dict = {'res_model': window.location.href.split('model=')[1].split('&')[0], 'title': this['title'], 'view_type': "form"}
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
        //this.help = true;
       
        this._rpc({
            model: 'erp.help',
            method: 'fetch_child_rec_help',
            args:[url_dict, parent_dict]
        })
        .then(function(res) {
            res_id = res.res_id
            action_name = res.action_name
            if(!action_name){
                var help_wizard=new HelpDialogue(self, 'Tags', self.size).open();
        //var textarea = help_wizard.$modal.find('#mytextarea')
        var textArea_id = "mytextarea";
        tinymce.remove("#mytextarea");

        tinyMCE.init({
            //******bind to textarea 
            selector: "#mytextarea",
            mode: "textareas",
            paste_as_text: true,
            plugins: ['paste link textcolor'],
            force_br_newlines: true,
            paste_remove_spans: true,
            toolbar:
    "undo redo | styleselect | fontselect | bold italic | alignleft aligncenter alignright alignjustify | outdent indent",
            menubar: false,
            font_formats:
    "Andale Mono=andale mono,times; Arial=arial,helvetica,sans-serif; Arial Black=arial black,avant garde; Book Antiqua=book antiqua,palatino; Comic Sans MS=comic sans ms,sans-serif; Courier New=courier new,courier; Georgia=georgia,palatino; Helvetica=helvetica; Impact=impact,chicago; Symbol=symbol; Tahoma=tahoma,arial,helvetica,sans-serif; Terminal=terminal,monaco; Times New Roman=times new roman,times; Trebuchet MS=trebuchet ms,geneva; Verdana=verdana,geneva; Webdings=webdings; Wingdings=wingdings,zapf dingbats",
            statusbar: false,
            browser_spellcheck: true,
            forced_root_block: "",
            setup: function (editor) {
                editor.on('init', function() {
                    var editor = tinymce.get('mytextarea'); // use your own editor id here - equals the id of your textarea
                    var content = editor.getContent();
                    tinymce.get("mytextarea").setContent(res.description);
                   $('#loading_gfx').css('display', 'none'); 
                });
            }
        });
        var tiny_mce = self.$modal[0].getElementsByClassName("textareafield")
        help_wizard.$el[8].style.display="none"
        var heading =help_wizard.$el[4].getElementsByClassName('main_heading')
        var input_heading = help_wizard.$el[4].getElementsByClassName('heading_input')
        heading[0].innerHTML=res.name
        
        input_heading[0].value=res.name
        input_heading[0].style.display="none"
        help_wizard.$el[6].innerHTML=res.description
        help_wizard.$el[10].innerHTML=res.help_id
        


            }else{ 
                if(res_id){
                    var help_wizard=new HelpDialogue(self, 'Tags', self.size).open();
        var textArea_id = "mytextarea";
        tinymce.remove("#mytextarea");

        tinyMCE.init({
            //******bind to textarea 
            selector: "#mytextarea",
            mode: "textareas",
            paste_as_text: true,
            plugins: ['paste link textcolor'],
            force_br_newlines: true,
            paste_remove_spans: true,
            toolbar:
    "undo redo | styleselect | fontselect | bold italic | alignleft aligncenter alignright alignjustify | outdent indent",
            menubar: false,
            font_formats:
    "Andale Mono=andale mono,times; Arial=arial,helvetica,sans-serif; Arial Black=arial black,avant garde; Book Antiqua=book antiqua,palatino; Comic Sans MS=comic sans ms,sans-serif; Courier New=courier new,courier; Georgia=georgia,palatino; Helvetica=helvetica; Impact=impact,chicago; Symbol=symbol; Tahoma=tahoma,arial,helvetica,sans-serif; Terminal=terminal,monaco; Times New Roman=times new roman,times; Trebuchet MS=trebuchet ms,geneva; Verdana=verdana,geneva; Webdings=webdings; Wingdings=wingdings,zapf dingbats",
            statusbar: false,
            browser_spellcheck: true,
            forced_root_block: "",
            setup: function (editor) {
                editor.on('init', function() {
                    var editor = tinymce.get('mytextarea'); // use your own editor id here - equals the id of your textarea
                    var content = editor.getContent();
                    tinymce.get("mytextarea").setContent(res.description);
                   $('#loading_gfx').css('display', 'none'); 
                });
            }
        });
        
        
        var tiny_mce = self.$modal[0].getElementsByClassName("textareafield")
        help_wizard.$el[8].style.display="none"
        var heading =help_wizard.$el[4].getElementsByClassName('main_heading')
        var input_heading = help_wizard.$el[4].getElementsByClassName('heading_input')
        heading[0].innerHTML=res.name
        
        input_heading[0].value=res.name
        input_heading[0].style.display="none"
        help_wizard.$el[6].innerHTML=res.description
        help_wizard.$el[10].innerHTML=res.help_id
        

                }else{
                    var help_wizard=new HelpDialogue(self, 'Tags', self.size).open();
        var textArea_id = "mytextarea";
        tinymce.remove("#mytextarea");

        tinyMCE.init({
            //******bind to textarea 
            selector: "#mytextarea",
            mode: "textareas",
            paste_as_text: true,
            plugins: ['paste link textcolor'],
            force_br_newlines: true,
            paste_remove_spans: true,
            toolbar:
    "undo redo | styleselect | fontselect | bold italic | alignleft aligncenter alignright alignjustify | outdent indent",
            menubar: false,
            font_formats:
    "Andale Mono=andale mono,times; Arial=arial,helvetica,sans-serif; Arial Black=arial black,avant garde; Book Antiqua=book antiqua,palatino; Comic Sans MS=comic sans ms,sans-serif; Courier New=courier new,courier; Georgia=georgia,palatino; Helvetica=helvetica; Impact=impact,chicago; Symbol=symbol; Tahoma=tahoma,arial,helvetica,sans-serif; Terminal=terminal,monaco; Times New Roman=times new roman,times; Trebuchet MS=trebuchet ms,geneva; Verdana=verdana,geneva; Webdings=webdings; Wingdings=wingdings,zapf dingbats",
            statusbar: false,
            browser_spellcheck: true,
            forced_root_block: "",
            setup: function (editor) {
                editor.on('init', function() {
                    var editor = tinymce.get('mytextarea'); // use your own editor id here - equals the id of your textarea
                    var content = editor.getContent();
                    tinymce.get("mytextarea").setContent(res.description);
                   $('#loading_gfx').css('display', 'none'); 
                });
            }
        });
        var tiny_mce = self.$modal[0].getElementsByClassName("textareafield")
        help_wizard.$el[8].style.display="none"
        var heading =help_wizard.$el[4].getElementsByClassName('main_heading')
        var input_heading = help_wizard.$el[4].getElementsByClassName('heading_input')
        heading[0].innerHTML=res.name
        
        input_heading[0].value=res.name
        input_heading[0].style.display="none"
        help_wizard.$el[6].innerHTML=res.description
        help_wizard.$el[10].innerHTML=res.help_id
        

                }
            }
            
        });   
 
    },
    destroy: function (options) {
        if (this.help) {
            return;
        }
        var element = document.getElementsByClassName('modal o_technical_modal show')
        if (element.length) {
            document.getElementsByClassName('modal o_technical_modal show')[0].style.display = 'block';
        }
        // Need to trigger before real destroy but if 'closed' handler destroys
        // the widget again, we want to avoid infinite recursion
        if (!this.__closed) {
            this.__closed = true;
            this.trigger('closed', options);
        }

        if (this.isDestroyed()) {
            return;
        }
        var isFocusSet = this._focusOnClose();

        this._super();

        $('.tooltip').remove(); //remove open tooltip if any to prevent them staying when modal has disappeared
        if (this.$modal) {
            this.$modal.modal('hide');
            this.$modal.remove();
        }

        var modals = $('body > .modal').filter(':visible');
        if (modals.length) {
            if (!isFocusSet) {
                modals.last().focus();
            }
            // Keep class modal-open (deleted by bootstrap hide fnct) on body to allow scrolling inside the modal
            $('body').addClass('modal-open');
        }
    }
});
});
