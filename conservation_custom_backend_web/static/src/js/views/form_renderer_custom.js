odoo.define('conservation_custom_backend_web.form_renderer_custom', function (require) {
"use strict";

    var FormRenderer = require('web.FormRenderer');
    var config = require('web.config');
    var core = require('web.core');
    var QWeb = core.qweb;
    var dom = require('web.dom');
    var view_dialogs = require('web.view_dialogs');
    var dialogs = require('web.view_dialogs');
    var ThreadWidget = require('mail.widget.Thread');
    var time = require('web.time');
    var Dialog = require('web.Dialog');
    var ORDER = {
        ASC: 1, // visually, ascending order of message IDs (from top to bottom)
        DESC: -1, // visually, descending order of message IDs (from top to bottom)
    };
    // var Dialog = require('web.Dialog');
    var _t = core._t;

    view_dialogs.FormViewDialog.extend({

        init: function (parent, options) {
            debugger

            this._super(parent, options);

        },

    })


    FormRenderer.include({
         _renderButtonBox: function (node) {
        var self = this;
        var $result = $('<' + node.tag + '>', { 'class': 'o_not_full' });
        var buttons = _.map(node.children, function (child) {
            if (child.tag === 'button') {
                return self._renderStatButton(child);
            } else {
                return self._renderNode(child);
            }
        });
        var buttons_partition = _.partition(buttons, function ($button) {
            return $button.is('.o_invisible_modifier');
        });
        var invisible_buttons = buttons_partition[0];
        var visible_buttons = buttons_partition[1];

        // Get the unfolded buttons according to window size
        var nb_buttons = [2, 2, 4, 6][config.device.size_class] || 7;
        var unfolded_buttons = visible_buttons.slice(0, nb_buttons).concat(invisible_buttons);

        // Get the folded buttons
        var folded_buttons = visible_buttons.slice(nb_buttons);
        if (folded_buttons.length === 1) {
            unfolded_buttons = buttons;
            folded_buttons = [];
        }

        // Toggle class to tell if the button box is full (CSS requirement)
        // var full = (visible_buttons.length > nb_buttons);
        // $result.toggleClass('o_full', full).toggleClass('o_not_full', !full);

        // Add the unfolded buttons
        _.each(unfolded_buttons, function ($button) {
            $button.appendTo($result);
        });

        // Add the folded buttons
        _.each(folded_buttons, function ($button) {
            $button.appendTo($result);
        });

        // Add the dropdown with folded buttons if any
        // if (folded_buttons.length) {
        //     $result.append(dom.renderButton({
        //         attrs: {
        //             class: 'oe_stat_button o_button_more dropdown-toggle',
        //             'data-toggle': 'dropdown',
        //         },
        //         text: _t("More"),
        //     }));

        //     var $dropdown = $("<div>", {'class': "dropdown-menu o_dropdown_more", role: "menu"});
        //     _.each(folded_buttons, function ($button) {
        //         $button.addClass('dropdown-item').appendTo($dropdown);
        //     });
        //     $dropdown.appendTo($result);
        // }

        this._handleAttributes($result, node);
        this._registerModifiers(node, this.state, $result);
        return $result;
    },



    });

    // REMOVE CANCEL BUTTON FROM DIALOG
    // Dialog.confirm = function (owner, message, options) {
    //     var buttons = [
    //         {
    //             text: _t("Ok"),
    //             classes: 'btn-primary',
    //             close: true,
    //             click: options && options.confirm_callback
    //         },
    //     ];
    //     return new Dialog(owner, _.extend({
    //         size: 'medium',
    //         buttons: buttons,
    //         $content: $('<div>', {
    //             text: message,
    //         }),
    //         title: _t("Confirmation"),
    //     }, options)).open();
    // };


    // MESSAGE CHANGED WHEN REDIRECT FROM CURRENT OBJECT(EDIT MODE TO OTHER MODEL
    // FormView.include({
    //     can_be_discarded: function(message) {
    //     if (!this.$el.is('.oe_form_dirty')) {
    //         return $.Deferred().resolve();
    //     }

    //     message = message || _t("Since this record has been modified, you must select SAVE or REVERT befores leaving this page.");

    //     var self = this;
    //     var def = $.Deferred();
    //     var options = {
    //         title: _t("Warning"),
    //         confirm_callback: function() {
    //             self.$el.removeClass('oe_form_dirty');
    //             this.on('closed', null, function() { // 'this' is the dialog widget
    //                 def.resolve();
    //             });
    //         },
    //         cancel_callback: function() {
    //             def.reject();
    //         },
    //     };
    //     var dialog = Dialog.confirm(this, message, options);
    //     dialog.$modal.on('hidden.bs.modal', function() {
    //         def.reject();
    //     });
    //     return def;
    // },


    // _actualize_mode: function(switch_to) {
    //     var mode = switch_to || this.get("actual_mode");
    //     if (! this.datarecord.id) {
    //         mode = "create";
    //     } else if (mode === "create") {
    //         mode = "edit";
    //     }

    //     var viewMode = (mode === "view");
    //     this.$el.toggleClass('o_form_readonly', viewMode).toggleClass('o_form_editable', !viewMode);

    //     this.render_value_defs = [];
    //     this.set({actual_mode: mode});

    //     if(!viewMode) {
    //        if (this.ViewManager.$el.context.baseURI.split('model=')[1].split('&')[0] !== 'sale.order'){
    //         this.autofocus();
    //        }
    //     }
    // },

    // })


    ThreadWidget.include({
        events: {
                'click .search_users ': '_onClickdata',
           },
        



        render: function (thread, options) {
            var self = this;
            var shouldScrollToBottomAfterRendering = false;
            if (this._currentThreadID === thread.getID() && this.isAtBottom()) {
                shouldScrollToBottomAfterRendering = true;
            }
            this._currentThreadID = thread.getID();


            // copy so that reverse do not alter order in the thread object
            var messages = _.clone(thread.getMessages({ domain: options.domain || [] }));

            var modeOptions = options.isCreateMode ? this._disabledOptions :
                                                     this._enabledOptions;

            // attachments ordered by messages order (increasing ID)
            this.attachments = _.uniq(_.flatten(_.map(messages, function (message) {
                return message.getAttachments();
            })));

            options = _.extend({}, modeOptions, options, {
                selectedMessageID: this._selectedMessageID,
            });

            // dict where key is message ID, and value is whether it should display
            // the author of message or not visually
            var displayAuthorMessages = {};

            // Hide avatar and info of a message if that message and the previous
            // one are both comments wrote by the same author at the same minute
            // and in the same document (users can now post message in documents
            // directly from a channel that follows it)
            var prevMessage;
            _.each(messages, function (message) {
                if (
                    // is first message of thread
                    !prevMessage ||
                    // more than 1 min. elasped
                    (Math.abs(message.getDate().diff(prevMessage.getDate())) > 60000) ||
                    prevMessage.getType() !== 'comment' ||
                    message.getType() !== 'comment' ||
                    // from a different author
                    (prevMessage.getAuthorID() !== message.getAuthorID()) ||
                    (
                        // messages are linked to a document thread
                        (
                            prevMessage.isLinkedToDocumentThread() &&
                            message.isLinkedToDocumentThread()
                        ) &&
                        (
                            // are from different documents
                            prevMessage.getDocumentModel() !== message.getDocumentModel() ||
                            prevMessage.getDocumentID() !== message.getDocumentID()
                        )
                    )
                ) {
                    displayAuthorMessages[message.getID()] = true;
                } else {
                    displayAuthorMessages[message.getID()] = !options.squashCloseMessages;
                }
                prevMessage = message;
            });

            if (modeOptions.displayOrder === ORDER.DESC) {
                messages.reverse();
            }
            if(thread._messages){
                for (var i=0;i<thread._messages.length;i++){
                this._rpc({
                    model: 'res.partner',
                    method: 'check_user_type',
                    args: [[thread._messages[i]._serverAuthorID[0]],i],
                }).then(function (data) {
                    //console.log("-------------------------------------sachinkumar",thread._messages[data[1]]._serverAuthorID,data,i)
                    thread._messages[data[0]]._serverAuthorID.push(data[1]);
                    if(data[0]==thread._messages.length-1){
                        self.final_result(self,thread,options,ORDER,time.getLangDatetimeFormat(),messages,displayAuthorMessages,shouldScrollToBottomAfterRendering)
                    }
                    
                    // return data;
                });
            
            }
        }
        else{
            this.$el.html(QWeb.render('mail.widget.Thread', {
                thread: thread,
                displayAuthorMessages: displayAuthorMessages,
                options: options,
                ORDER: ORDER,
                dateFormat: time.getLangDatetimeFormat(),
            }));

            // must be after mail.widget.Thread rendering, so that there is the
            // DOM element for the 'is typing' notification bar
            if (thread.hasTypingNotification()) {
                this.renderTypingNotificationBar(thread);
            }

            _.each(messages, function (message) {
                var $message = self.$('.o_thread_message[data-message-id="'+ message.getID() +'"]');
                $message.find('.o_mail_timestamp').data('date', message.getDate());

                self._insertReadMore($message);
            });

            if (shouldScrollToBottomAfterRendering) {
                this.scrollToBottom();
            }

            if (!this._updateTimestampsInterval) {
                this.updateTimestampsInterval = setInterval(function () {
                    self._updateTimestamps();
                }, 1000*60);
            }

            this._renderMessageMailPopover(messages);

        }

            
        },
        final_result: function (self,thread, options,ORDER,dateFormat,messages,displayAuthorMessages,shouldScrollToBottomAfterRendering) {
            this.$el.html(QWeb.render('mail.widget.Thread', {
                thread: thread,
                displayAuthorMessages: displayAuthorMessages,
                options: options,
                ORDER: ORDER,
                dateFormat: time.getLangDatetimeFormat(),
            }));

            // must be after mail.widget.Thread rendering, so that there is the
            // DOM element for the 'is typing' notification bar
            if (thread.hasTypingNotification()) {
                this.renderTypingNotificationBar(thread);
            }

            _.each(messages, function (message) {
                var $message = self.$('.o_thread_message[data-message-id="'+ message.getID() +'"]');
                $message.find('.o_mail_timestamp').data('date', message.getDate());

                self._insertReadMore($message);
            });

            if (shouldScrollToBottomAfterRendering) {
                this.scrollToBottom();
            }

            if (!this._updateTimestampsInterval) {
                this.updateTimestampsInterval = setInterval(function () {
                    self._updateTimestamps();
                }, 1000*60);
            }

            this._renderMessageMailPopover(messages);
        },
        _onClickdata: function () {
            console.log("-=-dkjdjfdfjkdk",this,this,self)
            var self=this;
            self._rpc({
                    model: 'res.users',
                    method: 'name_search',
                    kwargs: {
                        name: '',
                        args: '',
                        operator: "ilike",
                        limit: 160,
                        context: '',
                    },
                })
                .then(self._searchCreatePopup.bind(self, "search"));

        },
        _searchCreatePopup: function (view, ids, context) {
        console.log("--------------------------",view,this)
        var self = this;
        return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, {
            res_model: 'res.users',
            domain: '',
            context:'',
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: ids ? _.map(ids, function (x) { return x[0]; }) : undefined,
            initial_view: view,
            disable_multiple_selection: true,
            no_create: !self.can_create,
            on_selected: function (records) {
                console.log("---------------------==============",records)
                self.custom_set_values(records)
                // self.reinitialize(records[0]);
                // self.activate();
            }
        })).open();
    },
    custom_set_values: function (argument) {
        // body...
        console.log("-==--==-=--=-=-=-=--=-",argument,this)
    },
        });
    ThreadWidget.ORDER = ORDER;
    return ThreadWidget;

});
