odoo.define('product_variant_snippets.product_block', function (require) {
'use strict';

    var custom_contact = $('.custom_details');
    
    $(document).ready(function(){
        
        var ajax = require('web.ajax');
        var core = require('web.core');
        var _t = core._t;
        var _rpc = require('web.rpc');
        var rpc = require('web.rpc');

        var utils = require('web.utils');
        
        var $snippets = $('.product_variant_snippet');

        $($snippets).each(function() {
            var $product_selector = $snippets.find('.products_selector');
            if($snippets.find('.products_selector_id')[0].innerHTML){
                var product_selector = $product_selector;
                
                var selected_product = parseInt($snippets.find('.products_selector_id')[0].innerHTML)
                
                if (!selected_product){
                    return 0;
                };
                var current_snippet = $(product_selector).closest('.product_variant_snippet');
                $(current_snippet).closest('.o_editable').addClass('o_dirty');
                
                $(current_snippet).find('[name="product_tmpl_id"]').attr('value', selected_product)
                var params = {
                    model: 'product.product',
                    method: 'search_read',
                    domain: [['product_tmpl_id','=', selected_product]]
                }
                rpc.query(params, {async: false}).then(function(data){
                    var records=data
                    
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
                   
                    if (records[0].product_variant_ids.length == 1){
                         select.setAttribute("class", "form-control variant_ids_snippet d-none");
                    }
                    else{
                         select.setAttribute("class", "form-control variant_ids_snippet");
                    }
                    $(data_main).after(select);
                    var params = {
                        model: 'product.product',
                        method: 'search_read',
                        domain: [['product_tmpl_id','=', selected_product]]
                    }
                    rpc.query(params, {async: false}).then(function(data){
                        $(current_snippet).find('.snippet_product_name').html(data[0].name);;

                        if (data[0].product_description != false){
                            $(current_snippet).find('.snippet_product_temp_desc').html(data[0].product_description);
                        }
                        else{
                            $(current_snippet).find('.snippet_product_temp_desc').html("No Product Description.");
                        }


                    $(current_snippet).find('.snippet_desc_header').html(data[0].full_name);
                    if (data[0].pro_description_sale != false){
                        $(current_snippet).find('.snippet_product_desc').html(data[0].pro_description_sale);
                    }
                    else{
                        $(current_snippet).find('.snippet_product_desc').html("There is no description for that product.");
                    }
                    if(data[0].image_medium != false){
                        $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image_medium );
                    }
                    $(current_snippet).find('.currency_symbol').html(data[0].cur_symbol);
                    $(current_snippet).find('.currency_symbol').html(data[0].currency_symbol);
                    $(current_snippet).find('.product_price').html(data[0].cur_symbol+data[0].website_price);
                    $(current_snippet).find('.product_description').html(data[0].pro_description_sale);
                    });
                    
                    for (var key in data) {
                        if (data.hasOwnProperty(key)) {           
                            var option = document.createElement("option");
                             option.setAttribute("value", data[key][0]);
                             option.innerHTML = data[key][1];
                             select.appendChild(option);
                        }
                    }
                    var plus_quantity = $(current_snippet).find('.plus_quantity');
                     plus_quantity.on('click', function(){
                        var span_quatity=$(current_snippet).find('.qty_product');
                        var now_quantity=parseInt(span_quatity[0].innerHTML)+1
                        span_quatity.html(now_quantity)

                    });
                    var minus_quantity = $(current_snippet).find('.minus_quantity');
                     minus_quantity.on('click', function(){
                        var span_quatity=$(current_snippet).find('.qty_product');
                        if(parseInt(span_quatity[0].innerHTML) != 0){
                            var now_quantity=parseInt(span_quatity[0].innerHTML)-1
                            span_quatity.html(now_quantity)
                        }

                    });
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

                            if (data[0].product_description != false){
                                $(current_snippet).find('.snippet_product_temp_desc').html(data[0].product_description);
                            }
                            else{
                                $(current_snippet).find('.snippet_product_temp_desc').html("No Product Description.");
                            }


                            
                    $(current_snippet).find('.snippet_desc_header').html(data[0].full_name);
                    if (data[0].pro_description_sale != false){
                        $(current_snippet).find('.snippet_product_desc').html(data[0].pro_description_sale);
                    }
                    else{
                        $(current_snippet).find('.snippet_product_desc').html("There is no description for that product.");
                    }
                    if(data[0].image != false){
                        $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );
                    }
                    $(current_snippet).find('.currency_symbol').html(data[0].cur_symbol);
                    $(current_snippet).find('.currency_symbol').html(data[0].currency_symbol);
                    $(current_snippet).find('.product_price').html(data[0].cur_symbol+data[0].website_price);
                    $(current_snippet).find('.product_description').html(data[0].pro_description_sale);
                        });

                     });
                     var custom_add_to_cart_product = $(current_snippet).find('.custom_add_to_cart_product');
                     custom_add_to_cart_product.on('click', function(){
                        
                        var product_id=$(current_snippet).find('.variant_ids_snippet')[0].value
                        var quantity=$(current_snippet).find('.qty_product')[0].innerHTML
                        ajax.jsonRpc("/shop/cart/update_json", 'call', {
                        'product_id': parseInt(product_id),
                        'add_qty': parseInt(quantity) ,
                        }).then(function (data) {
                            var $cart_li_a = $('#top_menu li#my_cart_pop_over a');
                            $cart_li_a.find('.my_cart_quantity').text(data.cart_quantity);
                            ajax.jsonRpc('/fetch/current_cart', 'call', {
                        'name':'Website Header Icon Call Config Setting',
                        
                        }).then(function (data) {
                            var phone_popup=document.getElementById('phone-model')
                            phone_popup.style.display="none"
                            var email_popup=document.getElementById('email-model')
                            email_popup.style.display="none"
                            var modal = document.getElementById("phone-model");
                            var cart_modal = document.getElementById("cart-model");
                            console.log("------------------",data)
                            cart_modal.innerHTML=data
                            
                            
                              
                              
                              
                              modal.style.display = "none";
                              cart_modal.style.display = "block";
                        });
                        });

                    });
                     var custom_open_document = $(current_snippet).find('.js_check_product');
                     custom_open_document.on('click', function(){
                        var product_id=$(current_snippet).find('.variant_ids_snippet')[0].value;
                        ajax.jsonRpc("/shop/snippet/wizard", 'call', {
                        'product_id': parseInt(product_id),
                        
                        }).then(function (return_data) {
                            var modal = $(current_snippet).find('#myModal');
                            var inner_body = $(modal).find('.modal-content')[0];
                            inner_body.innerHTML=return_data

                            modal[0].style.display = "block";
                            var span =$(modal).find('.close'); 
                        span.on('click', function(){
                            var modal = $(this).find('#myModal');
                            var modal_view= $(current_snippet).find('#myModal');
                            modal_view[0].style.display = "none";
                        });
                        window.onclick = function(event) {
                          if (event.target == modal) {
                            modal.style.display = "none";
                          }
                        }
                        });

                        
                    
                    

                     });
                     

                       
                });

                
                });
}

            
            
            var data=$($snippets).find(".snippet_product_name")
            
            var product_variant_id = $(this).find('[name="product_variant_id"]').val();
            var product_tmpl_id = $(this).find('[name="product_tmpl_id"]').val();
            if(product_variant_id){
                change_product_block_as_per_product_id(product_variant_id, false, this);
            } else {
                change_product_block_as_per_product_id(product_tmpl_id, true, this);
            }
        });

        if($snippets.length) {
            $snippets.find('.js_add_cart_json').off('click').on('click', function(ev) {
                ev.preventDefault();
                var $link = $(ev.currentTarget);
                var $input = $link.parent().find("input");
                var min = parseFloat($input.data("min") || 0);
                var max = parseFloat($input.data("max") || Infinity);
                var quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val() || 0, 10);
                var $qty = $(this).siblings('.quantity');
                $qty.val(quantity > min ? (quantity < max ? quantity : max) : min);
            });
        }

        $('.custom_add_to_cart').off('click').on('click', function (event) {z
            if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
                event.preventDefault();
                var $btn = $(this);
                var $cart_li_a = $('#top_menu li#my_cart_pop_over a');
                var $form = $btn.closest('form');
                var pid = $form.find('.product_id').val() || $form.find('input[name="product_id"]:first').val(),
                    qty = $form.find('.quantity').val();
                if(!pid){
                    return;
                }
                var loading = '<span class="fa fa-cog fa-spin v_loading"/>';
                $btn.text(' Adding');
                $btn.prepend(loading);
                ajax.jsonRpc("/shop/cart/update_json", 'call', {
                        'product_id': parseInt(pid, 10),
                        'add_qty': parseInt(qty) || 1,
                    }).then(function (data) {
                        $cart_li_a.find('.my_cart_quantity').text(data.cart_quantity);
                        $.get("/shop/cart", {'type': 'popover'})
                            .then(function (data) {
                                $cart_li_a.popover({
                                    trigger: 'hover',
                                    placement: 'right',
                                    html: true,
                                    content: data
                                }).popover('show');
                                $cart_li_a.data("bs.popover").config.content =  data;
                                $('.my_custom_cart_popover').find('.popover-title').html(_t("Cart Summary <a href='#' class='close' data-dismiss='alert'>&times;</a>"))
                                $('.my_custom_cart_popover').find('.popover-content').html(data)
                                $btn.text('Add to Cart');
                                $btn.find('.v_loading').remove();
                                $cart_li_a.popover("show");
                                $(".popover").css('position', "fixed");
                                $(".popover").on("mouseleave", function () {
                                    $cart_li_a.trigger('mouseleave');
                                });
                                setTimeout(function() {
                                    $cart_li_a.popover("hide");
                                }, 2000);
                            });
                    });
            }
            if ($(this).hasClass('a-submit-disable')){
                $(this).addClass("disabled");
            }
            if ($(this).hasClass('a-submit-loading')){
                var loading = '<span class="fa fa-cog fa-spin"/>';
                var fa_span = $(this).find('span[class*="fa"]');
                if (fa_span.length){
                    fa_span.replaceWith(loading);
                }
                else{
                    $(this).append(loading);
                }
            }
        });
        $('#product_more_info').on("click", function(e){
            var $form = $(this).closest('form');
            var product_id = $form.find('.product_id').val() || $form.find('input[name="product_id"]:first').val()
            var modal_id = "#product_more_info_modal_"+product_id
            $(modal_id).modal("show");
        });
        
        function get_image_path(model, id, img_type){
            img_type = (img_type) ? img_type : 'image';
            return "/web/image/" + model + "/" + id + "/" + img_type;
        }

        function price_to_str(price) {
            var l10n = _t.database.parameters;
            var precision = 2;

            if ($(".decimal_precision").length) {
                precision = parseInt($(".decimal_precision").last().data('precision'));
                if (!precision) { precision = 0; } //todo: remove me in master/saas-17
            }
            var formatted = _.str.sprintf('%.' + precision + 'f', price).split('.');
            formatted[0] = utils.insert_thousand_seps(formatted[0]);
            return formatted.join(l10n.decimal_point);
        }

        function change_product_block_as_per_product_id(product_id, is_product_template, snippet){
            var self = this;
            var model, product_product_id;
            var product_template_id = $(snippet).find('[name="product_tmpl_id"]').val();
            if (is_product_template){
                model = 'product.template';
                product_product_id = false;
            } else {
                model = 'product.product';
                product_product_id = product_id;
            }
            ajax.jsonRpc("/get-product-detail-from-id", 'call', {
                'model': model,
                'product_id': product_id,
            }).then(function (data) {
                if(data.length > 0){
                    var record = data[0];
                    $(snippet).find('.snippet_product_name').html(record.website_name || record.name || '');
                    $(snippet).find('.snippet_product_temp_desc').html(record.product_description || '');
                    $(snippet).find('.snippet_desc_header').html(record.display_name || '');
                    $(snippet).find('.snippet_product_desc').html(record.pro_description_sale || '');
                    $(snippet).find('.currency_symbol').html(record.currency_symbol || '');
                    $(snippet).find('.currency_amount').html(price_to_str(record.website_price) || '');
                    // $(snippet).find('.product_big_image img').attr('src', get_image_path(model, product_id, 'image'));
                    $(snippet).find('.product-page-url').attr('href', '/shop/product/' + product_template_id + '?' + 'variant-id=' + (product_product_id || record.product_variant_id[0] || ''))
                }
            });

            
        }

        
    });
});
