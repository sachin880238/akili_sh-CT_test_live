odoo.define('product_variant_snippets.product_variant_snippets', function (require) {
'use strict';
    var ajax = require('web.ajax');
    var core = require('web.core');
    var sAnimations = require('website.content.snippets.animation');
    var _t = core._t;
    var rpc = require('web.rpc');
    var options = require("web_editor.snippets.options");
    var context = require('web_editor.context');
    var productModel = 'product.template';


    

    options.registry.product_variant_snippet = options.Class.extend({

        start: function(){
            var self=this;
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
                                fields: ['default_code', 'name'],
                                context: context.get
                            }
                        });
                    }
                )
            );

            $product_selector.on('change', function(){
                var product_selector = this;
                
                var selected_product = $(product_selector).select2('data');
                
                if (!selected_product){
                    return 0;
                };
                var current_snippet = $(product_selector).closest('.product_variant_snippet');
                $(current_snippet).closest('.o_editable').addClass('o_dirty');
                $(current_snippet).find('[name="product_tmpl_id"]').attr('value', selected_product.id)
                var params = {
                    model: 'product.product',
                    method: 'search_read',
                    domain: [['product_tmpl_id','=', selected_product.id]]
                }
                rpc.query(params, {async: false}).then(function(data){
                    if (data[0].product_variant_ids.length == 1){
                    $(current_snippet).find('.snippet_product_name').html(data[0].name);;
                    $(current_snippet).find('.products_selector_id').html(this.value);
                    $(current_snippet).find('.products_selector_id').html(selected_product.id);
                    $(current_snippet).find('.snippet_desc_header').html(data[0].full_name);
                    if (data[0].description_sale != false){
                        $(current_snippet).find('.snippet_product_desc').html(data[0].description_sale);
                    }
                    else{
                        $(current_snippet).find('.snippet_product_desc').html("There is no description for that product.");
                    }
                    $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );
                    $(current_snippet).find('.currency_symbol').html(data[0].cur_symbol);
                    $(current_snippet).find('.currency_symbol').html(data[0].currency_symbol);
                    $(current_snippet).find('.product_price').html((data[0].website_price));
                    $(current_snippet).find('.product_description').html(data[0].description_sale);

                    var selection_variant = $(current_snippet).find('.variant_ids_snippet')
                    if(selection_variant.length >=0){
                        $(selection_variant).remove()
                    }
                    }
                else{
                    ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                    model:  'product.product',
                    method: 'search_product_variants',
                    args: [],
                    kwargs: {
                        product_template_id:selected_product
                    }
                }).then(function (data) {
                    var selection_variant = $(current_snippet).find('.variant_ids_snippet')
                    if(selection_variant.length >=0){
                        $(selection_variant).remove()
                    }
                    var data_main=$(current_snippet).find(".variant_description_div")
                    var selection_variant = $(current_snippet).find('.selection-variant-id').empty();
                    var select = document.createElement("select");
                    select.setAttribute("name", "selectChildren");
                    select.setAttribute("class", "form-control variant_ids_snippet");
                    $(data_main).after(select);
                    var params = {
                        model: 'product.product',
                        method: 'search_read',
                        domain: [['product_tmpl_id','=', selected_product.id]]
                    }
                    rpc.query(params, {async: false}).then(function(data){
                        $(current_snippet).find('.snippet_product_name').html(data[0].name);;
                    $(current_snippet).find('.snippet_desc_header').html(data[0].full_name);
                    $(current_snippet).find('.products_selector_id').html(selected_product.id);
                    if (data[0].description_sale != false){
                        $(current_snippet).find('.snippet_product_desc').html(data[0].description_sale);
                    }
                    else{
                        $(current_snippet).find('.snippet_product_desc').html("There is no description for that product.");
                    }
                    $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );
                    $(current_snippet).find('.currency_symbol').html(data[0].cur_symbol);
                    $(current_snippet).find('.currency_symbol').html(data[0].currency_symbol);
                    $(current_snippet).find('.product_price').html((data[0].website_price));
                    $(current_snippet).find('.product_description').html(data[0].description_sale);
                    });
                    
                    for (var key in data) {
                        if (data.hasOwnProperty(key)) {           
                            var option = document.createElement("option");
                             option.setAttribute("value", data[key][0]);
                             option.innerHTML = data[key][1];
                             select.appendChild(option);
                        }
                    }
                    var selection_variant_list = $(current_snippet).find('.variant_ids_snippet');
                    if(!selection_variant_list){
                        return 0;
                    }
                     selection_variant_list.on('change', function(){
                        var current_snippet = $(selection_variant_list).closest('.product_variant_snippet');
                        var params = {
                            model: 'product.product',
                            method: 'search_read',
                            domain: [['id','=', parseInt(this.value)]]
                        }
                        rpc.query(params, {async: false}).then(function(data){
                            $(current_snippet).find('.snippet_product_name').html(data[0].name);;
                    $(current_snippet).find('.snippet_desc_header').html(data[0].full_name);
                    if (data[0].description_sale != false){
                        $(current_snippet).find('.snippet_product_desc').html(data[0].description_sale);
                    }
                    else{
                        $(current_snippet).find('.snippet_product_desc').html("There is no description for that product.");
                    }
                    $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );
                    $(current_snippet).find('.currency_symbol').html(data[0].cur_symbol);
                    $(current_snippet).find('.currency_symbol').html(data[0].currency_symbol);
                    $(current_snippet).find('.product_price').html((data[0].website_price));
                    $(current_snippet).find('.product_description').html(data[0].description_sale);
                        });

                     });

                });

                }

                });

            });
        },
        

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

    });

});
