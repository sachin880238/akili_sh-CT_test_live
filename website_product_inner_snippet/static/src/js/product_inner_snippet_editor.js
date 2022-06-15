odoo.define('website_product_inner_snippet.product_inner_snippet', function (require) {
'use strict';
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    $(document).ready(function(){

    var options = require("web_editor.snippets.options");
    var context = require('web_editor.context');
    var base = require('web_editor.base');
    var rpc = require('web.rpc');
    var productModel = 'product.template';

    // This function will be automatically called after defining snippet options.
    options.registry.js_editor_inner_snippet = options.Class.extend({

        start: function(){
            this._super();
            var $div = this.$target.find('.product-selector-placeholder');
            this.set_variant_selection($div);
        },

        set_variant_selection: function ($div) {
            var self =  this;
            var $product_selector = this.$target.find('.products_selector:first');
            $product_selector.select2(
                this.product_selector_wrapper(_t('Pick a product'), false,
                    function () {
                        return ajax.jsonRpc("/web/dataset/call_kw", 'call', {
                            model:  productModel,
                            method: 'search_read',
                            args: [],
                            kwargs: {
                                domain: [('', '', (['website_published','=',true]))],
                                fields: ['default_code', 'name'],
                                context: context.get
                            }
                        });
                    }
                )
            );

            $product_selector.on('change', function(){
                self.change_selected_product_editable_mode(this);
            })
        },

        // START SELECT WRAPPER OF PRODUCT SELECTION
        product_selector_wrapper: function (tag, multi, fetch_fnc) {
            var self = this;
            return {
                width: '100%',
                placeholder: tag,
                allowClear: true,
                formatNoMatches: false,
                multiple: multi,
                selection_data: false,
                fetch_rpc_fnc : fetch_fnc,
                formatResult: function (product) {
                    return $(
                      "<span><img height='24px' width='24px' src='" + self.get_product_img_path(product.id, 'image_small') + "'/> " + product.text + "</span>"
                    );
                },
                formatSelection: function (data) {
                    if (data.tag) {
                        data.text = data.tag;
                    }
                    return data.text;
                },
                fill_data: function (query, data) {
                    var that = this,
                        tags = {results: []};
                    _.each(data, function (obj) {
                        if (that.matcher(query.term, obj.name)) {
                            tags.results.push({id: obj.id, text: obj.name});
                        }
                    });
                    query.callback(tags);
                },
                query: function (query) {
                    var that = this;
                    if (!this.selection_data) {
                        this.fetch_rpc_fnc().then(function (data) {
                            var res = [];
                            _.each(data, function(product){
                                var display_name = product.default_code ? '[' + product.default_code + '] ' + product.name : product.name;
                                res.push({id: product.id, name: display_name})
                            })
                            that.fill_data(query, res);
                            that.selection_data = res;
                        });
                    } else {
                        this.fill_data(query, this.selection_data);
                    }
                }
            };
        },

        get_product_img_path: function(product_id, img_type){
            img_type = (img_type) ? img_type : 'image';
            return "/web/image/" + productModel + "/" + product_id + "/" + img_type;
        },
        // END SELECT WRAPPER OF PRODUCT SELECTION

        // START ONCHANGE OF EDITABLE SNIPPET CHANGE PRODUCT
        change_selected_product_editable_mode: function (selected_product_html) {
            var self = this;
            var selected_product = $(selected_product_html).select2('data');
            
            if (!selected_product){
                console.log("Not any product Selected!!")
                return 0;
            };
                
            var current_snippet = $(selected_product_html).closest('.s_inner_snippet');
            $(current_snippet).closest('.o_editable').addClass('o_dirty');
                
            $(current_snippet).find('[name="product_tmpl_id"]').attr('value', selected_product.id)

            $(current_snippet).find('.inner_snippet_selection').addClass('d-none');

            var params = {
                    model: 'product.product',
                    method: 'search_read',
                    domain: [['product_tmpl_id','=', selected_product.id]]
                }
            rpc.query(params, {async: false}).then(function(data){    
                $(current_snippet).find('.product_variant_length').val(data.length);
                if (data.length == 1){

                    $(current_snippet).find('.snippet_product_name').html(data[0].name);;
                    $(current_snippet).find('.snippet_product_temp_desc').html(data[0].product_description);
                    $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );
                    
                    $(current_snippet).find('.product_id').val(data[0].id);
                    $(current_snippet).find('.product_display_name').html((data[0].display_name));
                    $(current_snippet).find('.product_description_sale').html(data[0].description_sale);
                    $(current_snippet).find('.currency_symbol').html(data[0].currency_symbol);
                    $(current_snippet).find('.currency_amount').html((data[0].website_price));
                    $(current_snippet).find('.inner_snippet_description_div').removeClass('d-none');
                    $(current_snippet).find('.inner_snippet_description_div label').addClass('d-none');
                    $(current_snippet).find('.inner_snippet_action_block').removeClass('d-none');
                    $(current_snippet).find('.inner_snippet_dropdown').addClass('d-none');
                } else {
                    if (data[0].website_selection == 'selection'){
                        var selection_variant = $(current_snippet).find('[name="inner_snippet_selection"]').empty();
                        
                        $(current_snippet).find('.snippet_product_name').html(data[0].name);;
                        $(current_snippet).find('.snippet_product_temp_desc').html(data[0].product_description);
                        $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );

                        $(current_snippet).find('.inner_snippet_selection').removeClass('d-none');
                        $(current_snippet).find('.inner_snippet_dropdown').addClass('d-none');
                        $(current_snippet).find('.inner_snippet_description_div').addClass('d-none');
                        $(current_snippet).find('.inner_snippet_action_block').addClass('d-none');

                        var record = data[0];
                        if (data.length >1){
                            $('<option class="select-placeholder" value="">Select</option>').appendTo(selection_variant);
                        }
                        for (var i = 0; i < data.length; ++i){
                            $("<option></option>", {value: data[i].id, text: data[i].display_name}).appendTo(selection_variant);
                        }
                    } else {
                        self.multiple_dropdown_product(current_snippet, data);
                    }
                }
            });

        },

        multiple_dropdown_product: function(current_snippet, data){
            var attribute_line_ids = data[0].attribute_line_ids
            var product_tmpl_id = data[0].product_tmpl_id[0]

            ajax.jsonRpc("/get-atttribute-detail-from-template", 'call', {
                'product_tmpl_id': data[0].product_tmpl_id[0],
            }).then(function (result) {
                var product_attr_selection = result['product_attr_selection']
                var html = ''
                $.each(product_attr_selection, function(k, v) {
                    html += '<div class="mt8">'
                    
                        html += '<label class="control-label" for="email">'+k+'</label>'
                        html += '<select class="form-control inner_snippet_dropdown" name="attribute-'+product_tmpl_id+'-'+v[0]+'" id='+v[0]+'>'
                        html += '<option class="select-placeholder" value="">Select</option>'
                        for (var i=0; i<v[1].length; i++){
                            html += "<option value='"+v[1][i][0]+"'>"+v[1][i][1]+"</option>"
                        }
                        html += '</select>'
                    
                    html += '</div>'
                });
                
                $(current_snippet).find('.snippet_product_name').html(data[0].name);;
                $(current_snippet).find('.snippet_product_temp_desc').html(data[0].product_description);
                $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );
                $(current_snippet).append('<input class="attribiute_selection" type="hidden"/>')
                $(current_snippet).find('.inner_snippet_dropdown').removeClass('d-none');
                $(current_snippet).find('.inner_snippet_dropdown_ul').empty();
                $(current_snippet).find('.inner_snippet_dropdown_ul').append(html);
                $(current_snippet).find('.product_tmpl_id').val(product_tmpl_id);
                $(current_snippet).find('.inner_snippet_description_div').addClass('d-none');
                $(current_snippet).find('.inner_snippet_action_block').addClass('d-none');
            });
        }
        // END ONCHANGE OF EDITABLE SNIPPET CHANGE PRODUCT
    });
    });
});
