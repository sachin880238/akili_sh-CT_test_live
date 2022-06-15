odoo.define('website_product_inner_snippet.action_block', function (require) {
'use strict';

    $(document).ready(function(){
        var ajax = require('web.ajax');
        var core = require('web.core');
        var _t = core._t;
        var rpc = require('web.rpc');

        var utils = require('web.utils');

        $('.custom_add_to_cart').off('click').on('click', function (event) {
            console.log("aaaaaa-----------------------------------------------aaaaaaa")
            if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
                event.preventDefault();
                var $btn = $(this);
                var $cart_li_a = $('#top_menu li#my_cart_pop_over a');
                var $form = $btn.closest('form');
                var pid = $form.find('.product_id').val() || $form.find('input[name="product_id"]:first').val(),
                    qty = $form.find('.quantity').val();

                    console.log("aaaaaa-----------bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",qty,pid)
                    console.log("aaaaaa-----------bbbbbbbbbbcccccccccccccccccccccccccccc",this)
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
                        // $.get("/shop/cart", {'type': 'popover'})
                        ajax.jsonRpc('/fetch/current_cart', 'call', {
                        'name':'Website Header Icon Call Config Setting',
                        
                        })
                            // .then(function (data) {
                            //     $cart_li_a.popover({
                            //         trigger: 'hover',
                            //         placement: 'right',
                            //         html: true,
                            //         content: data
                            //     }).popover('show');
                            //     $cart_li_a.data("bs.popover").config.content =  data;
                            //     $('.my_custom_cart_popover').find('.popover-title').html(_t("Cart Summary <a href='#' class='close' data-dismiss='alert'>&times;</a>"))
                            //     $('.my_custom_cart_popover').find('.popover-content').html(data)
                            //     $btn.text('Add to Cart');
                            //     $btn.find('.v_loading').remove();
                            //     // $cart_li_a.popover("show");
                            //     $(".popover").css('position', "fixed");
                            //     $(".popover").on("mouseleave", function () {
                            //         $cart_li_a.trigger('mouseleave');
                            //     });
                            //     setTimeout(function() {
                            //         $cart_li_a.popover("hide");
                            //     }, 2000);
                            // });
                        .then(function (data) {
                            $btn.text('Add to Cart');
                            $btn.find('.v_loading').remove();
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

        $('.custom_add_to_cart_bundle').off('click').on('click', function (event) {
            console.log("aaaaaa-----------------------------------------------aaaaaaa")
            if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
                event.preventDefault();
                var $btn = $(this);
                var $cart_li_a = $('#top_menu li#my_cart_pop_over a');
                var $form = $btn.closest('form');
                var b_id = $form 
                var bom_id = $form.find('.select.form-control')
                var bom;
                for (bom in bom_id){
//                    console.log("------------------------------",bom)
                }

                var pid = $form.find('.product_id').val() || $form.find('input[name="product_id"]:first').val(),
                    qty = $form.find('.quantity').val();

                var div_container_bomb = document.getElementById("variant_description_div_"+pid)
                var limit_field=div_container_bomb.getElementsByClassName("hidden_for_type_input_field")[0]
                console.log("=============================",pid,limit_field)
                console.log('run',limit_field,limit_field.value,div_container_bomb)
                if(limit_field!=null){
                console.log('--------------->>>>heello')
                limit_field=limit_field.value
                }
                var data = document.getElementsByName("add_qty_bomb");
                console.log('-------------->>>>>>>',limit_field,data)
                var quantity_bomb=[]
                var variant_ids=[]
                for(var i=0;i<parseInt(limit_field);i++){
                    var qty_bomb = div_container_bomb.getElementsByClassName("add_qty_bomb")[i].value;
                    console.log("qty_bomb-----------44444444444444444444",qty_bomb,i)
                    var variant_id = div_container_bomb.getElementsByClassName("variant_select")[i].value;
                    qty_bomb=parseInt(qty_bomb)*parseInt(qty)
                    quantity_bomb.push(qty_bomb)
                    variant_ids.push(variant_id)
                }


                    console.log('-----------------------qty_data',quantity_bomb,variant_ids)


                    console.log("aaaaaa-----------ddddddddddddddddddd",b_id)
                    console.log("aaaaaa-----------ddddddddddddddddddd",bom_id,pid)
                    
                if(!pid){
                    return;
                }
                var loading = '<span class="fa fa-cog fa-spin v_loading"/>';
                $btn.text(' Adding');
                $btn.prepend(loading);
                console.log('--------------->>>>',qty)
                ajax.jsonRpc("/shop/cart/update_json", 'call', {
                        'product_id': parseInt(pid, 10),
                        'add_qty': parseInt(qty) || 1,
                        'variant_quantity':quantity_bomb,
                        'variant_ids':variant_ids
                    }).then(function (data) {
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
                        cart_modal.innerHTML=data
                        
                        
                          
                          
                          
                          modal.style.display = "none";
                          cart_modal.style.display = "block";
                          $btn.text('Add to Cart');
                        $btn.find('.v_loading').remove();
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


        // end custom add to cart


        // var Model = require('web.Model')

        var $snippets = $('.s_inner_snippet');

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
        var current_snippet = $snippets
        if($snippets.length) {
            for(var i=0;i<$snippets.length;i++){
                var option_type=$($snippets[i]).find('.attribiute_selection')
                var products_selector = $($snippets[i]).find("input.products_selector")
                console.log("----------ssss----------------------------->>>>>>>>>",option_type)
                
                    var params = {
                    model: 'product.product',
                    method: 'search_read',
                    domain: [['product_tmpl_id','=', parseInt(products_selector[0].value)]]
                }
            rpc.query(params, {async: false}).then(function(data){ 
                if(option_type.length==0){
                console.log("------------------",$snippets[i])
                $($snippets[i]).find('.product_variant_length').val(data.length);
                if (data.length == 1){

                    $($snippets[i]).find('.snippet_product_name').html(data[0].name);;
                    $($snippets[i]).find('.snippet_product_temp_desc').html(data[0].product_description);
                    $($snippets[i]).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );
                    
                    $($snippets[i]).find('.product_id').val(data[0].id);
                    $($snippets[i]).find('.product_display_name').html((data[0].display_name));
                    $($snippets[i]).find('.product_description_sale').html(data[0].description_sale);
                    $($snippets[i]).find('.currency_symbol').html(data[0].currency_symbol);
                    $($snippets[i]).find('.currency_amount').html((data[0].website_price));
                    $($snippets[i]).find('.inner_snippet_description_div').removeClass('d-none');
                    $($snippets[i]).find('.inner_snippet_description_div label').addClass('d-none');
                    $($snippets[i]).find('.inner_snippet_action_block').removeClass('d-none');
                    $($snippets[i]).find('.inner_snippet_dropdown').addClass('d-none');
                } else {
                    
                        var selection_variant = $($snippets[i]).find('[name="inner_snippet_selection"]').empty();
                        
                        
                        var record = data[0];
                        if (data.length >1){
                            $('<option class="select-placeholder" value="">Select</option>').appendTo(selection_variant);
                        }
                        for (var j = 0; j < data.length; ++j){
                            console.log("ggggggggggggggggggggggg",data[i].is_published)
                            if(data[j].unpublish_product != true){
                            $("<option></option>", {value: data[j].id, text: data[j].display_name}).appendTo(selection_variant);
                        }}
                    } }
                    else{
                        var attribute_line_ids = data[0].attribute_line_ids
            var product_tmpl_id = data[0].product_tmpl_id[0]
            console.log("------------------",$snippets[i],product_tmpl_id,i)
            ajax.jsonRpc("/get-atttribute-detail-from-template", 'call', {
                'product_tmpl_id': data[0].product_tmpl_id[0],'seq':i
            }).then(function (result) {
                console.log("===============================dddddddddddddd",$snippets[result.seq],product_tmpl_id,result)
                var product_attr_selection = result['product_attr_selection']
                console.log("9999999999999999998888888888888888888888",product_attr_selection)
                var html = ''
                $.each(product_attr_selection, function(k, v) {
                    console.log("---------------------------------------->>>",k,v,v[1])
                    html += '<div class="mt8">'
                    
                        console.log("-------------------------------kk",k,v)
                        html += '<label class="control-label" for="email">'+k+'</label>'
                        html += '<select class="form-control inner_snippet_dropdown" name="attribute-'+product_tmpl_id+'-'+v[0]+'" id='+v[0]+'>'
                        html += '<option class="select-placeholder" value="">Select</option>'
                        for (var i=0; i<v[1].length; i++){
                            html += "<option value='"+v[1][i][0]+"'>"+v[1][i][1]+"</option>"
                        }
                        html += '</select>'
                    
                    html += '</div>'
                });
                console.log("---------------------------------------",html)
                $($snippets[result.seq]).find('.snippet_product_name').html(data[0].name);;
                $($snippets[result.seq]).find('.snippet_product_temp_desc').html(data[0].product_description);
                $($snippets[result.seq]).find('.variant_img').attr("src","data:image/jpeg;base64,"+data[0].image );

                $($snippets[result.seq]).find('.inner_snippet_dropdown').removeClass('d-none');
                console.log("fffffffffffffffffffffffffffffffffffffff",$snippets[i],$($snippets[i]).find('.inner_snippet_dropdown_ul'))
                $($snippets[result.seq]).find('.inner_snippet_dropdown_ul').empty();
                $($snippets[result.seq]).find('.inner_snippet_dropdown_ul').append(html);
                $($snippets[result.seq]).find('.product_tmpl_id').val(product_tmpl_id);
                $($snippets[result.seq]).find('.inner_snippet_description_div').addClass('d-none');
                $($snippets[result.seq]).find('.inner_snippet_action_block').addClass('d-none');
            });
        }
            });
                

            }
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
        
        // START CODE FOR CHANGE SELECTION DROPDOWN
        $('[name="inner_snippet_selection"]').change(function(){
            var current_snippet = $(this).closest('.s_inner_snippet');
            var product_id = $(this).val()

            if (product_id){
                ajax.jsonRpc("/get-product-detail-from-id", 'call', {
                    'model': 'product.product',
                    'product_id': parseInt(product_id),
                }).then(function (data) {
                    if(data.length > 0){
                        var record = data[0];
                        if(record.image_medium != false){
                            $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+record.image_medium );
                        }
                        $(current_snippet).find('.product_id').val(record.id);
                        $(current_snippet).find('.product_display_name').html(record.full_name || '');
                        $(current_snippet).find('.product_description_sale').html(record.description_sale || '');
                        $(current_snippet).find('.currency_symbol').html(record.currency_symbol || '');
                        $(current_snippet).find('.currency_amount').html(price_to_str(record.website_price) || '');
                        $(current_snippet).find('.inner_snippet_description_div').removeClass('d-none');
                        $(current_snippet).find('.inner_snippet_description_div label').removeClass('d-none');
                        $(current_snippet).find('.inner_snippet_action_block').removeClass('d-none');
                    }
                });
            } else {
                $(current_snippet).find('.inner_snippet_description_div').addClass('d-none');
                $(current_snippet).find('.inner_snippet_action_block').addClass('d-none');
            }
        })
        // END CODE FOR CHANGE SELECTION DROPDOWN
        

        // START CODE FOR CHANGE ATTRIBUTES DROPDOWN
        $('.inner_snippet_dropdown').change(function(event){
            console.log("----------------------request",this,$(event.target).attr("id"))
            var current_snippet = $(this).closest('.s_inner_snippet');
            var product_tmpl_id = $(current_snippet).find('.product_tmpl_id').val()
            console.log("---------------------",current_snippet)
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                    model:  'product.template',
                    method: 'get_posible_combi',
                    args: [],
                    kwargs: {
                        product_template_id:product_tmpl_id,
                        attribute_value_id:$(event.target).find(":selected").val(),
                        attribute_id:$(event.target).attr("id"),

                    }
                }).then(function (combinationData) {
                    if(event.currentTarget.value != 'none'){
                    for(var j=0;j<Object.keys(combinationData.final_dict).length;j++){
                        var select_field_name='attribute-'+combinationData.product_template_id+"-"+Object.keys(combinationData.final_dict)[j];
                        console.log("-------------------------------",current_snippet[0],select_field_name)
                        var x = current_snippet.find('select[name="'+select_field_name+'"]');
                        console.log("fffffffffffffffffffffffff",x[0].options)
                        console.log("fffffffffffffffffffffffff-------------------",x[0].value)
                        var value_data=x[0].value
                        
                        
                        x[0].options.length=1
                        console.log("ggggggggggggggggggggggggggg",x[0].options)
                        for(var k=0;k<combinationData.final_dict[Object.keys(combinationData.final_dict)[j]].length;k++){
                            console.log("888888888888888888888888888888888")
                            var option =document.createElement("option");
                            console.log("8888888888888888888888888888888881111")
                            option.text = combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][k][1]+" "+combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][k][2];
                            console.log("888888888888888888888888888888888222222222222",combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][k][0],combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][k])
                            option.value=combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][k][0];
                            console.log("gggggggggggfffffffffffffffffffff",option,x)
                            x[0].add(option);
                            console.log("fffffffffffff")
                            x[0].value=value_data
                            
                        }
                        // if(combinationData.combination[Object.keys(combinationData.final_dict)[j]-1]!=null){
                        //     console.log("------------------",combinationData.combination,Object.keys(combinationData.final_dict),combinationData.combination,combinationData.combination[Object.keys(combinationData.final_dict)[j]-1])
                        //     x[0].value=combinationData.combination[j]
                        // }
                    }}
                    if(product_tmpl_id){
                        var values = [];
                        $(current_snippet).find('select.inner_snippet_dropdown').each(function() {
                        console.log("--------------------------------------------",$(this).val(),this)
                        values.push(+$(this).val());
                    });
                ajax.jsonRpc("/get-attribute-value-from-tmpl-id", 'call', {
                    'product_tmpl_id': parseInt(product_tmpl_id),'collect_comb':values
                }).then(function (data) {
                    console.log("----------=================---------------",data)
                     if (data[1]!=false) {
                            change_product_by_attribute(current_snippet, data[1].product_id);
                            
                        } else {
                            $(current_snippet).find('.inner_snippet_description_div').addClass('d-none');
                            $(current_snippet).find('.inner_snippet_action_block').addClass('d-none');
                        }
                    // console.log("gggggggggggggggg--------------------------",data,current_snippet.find('select.inner_snippet_dropdown'))

                    // var variant_ids = data;
                    
                    
                    

                    // for (var k in variant_ids) {
                    //     console.log("ffffffffffffffdddddddddddddddddddddddd",k,variant_ids[k][1],values)
                    //     console.log("ffffffffffffddddddddddddddddddddddddddddssssssssssss",_.isEmpty(_.difference(variant_ids[k][1], values)))
                       
                    // }
                });
            }
            });

            
            
        });

        function change_product_by_attribute(current_snippet, variant_id){
            console.log("ggggggggggggg----------------------------",current_snippet,variant_id)
            ajax.jsonRpc("/get-product-detail-from-id", 'call', {
                'model': 'product.product',
                'product_id': variant_id,
            }).then(function (data) {
                if(data.length > 0){
                    var record = data[0];
                    if(record.image_medium != false){
                        $(current_snippet).find('.variant_img').attr("src","data:image/jpeg;base64,"+record.image_medium );
                    }
                    $(current_snippet).find('.product_id').val(record.id);
                    $(current_snippet).find('.product_display_name').html(record.full_name || '');
                    $(current_snippet).find('.product_description_sale').html(record.description_sale || '');
                    $(current_snippet).find('.currency_symbol').html(record.currency_symbol || '');
                    $(current_snippet).find('.currency_amount').html(price_to_str(record.website_price) || '');
                    $(current_snippet).find('.inner_snippet_description_div').removeClass('d-none');
                    $(current_snippet).find('.inner_snippet_description_div label').removeClass('d-none');
                    $(current_snippet).find('.inner_snippet_action_block').removeClass('d-none');
                }
            });
        }

        // END CODE FOR CHANGE ATTRIBUTES DROPDOWN

        // START CODE FOR MORE INFO BUTTON
        $('.inner_snippet_more_info').click(function(){
            var current_snippet = $(this).closest('.s_inner_snippet');
            var product_id = $(current_snippet).find('[name="product_id"]').val();

            ajax.jsonRpc("/get-doc-detail-from-product-id", 'call', {
                'product_id': parseInt(product_id),
            }).then(function (data) {
                if (data.have_published_document){
                    $(current_snippet).find('.document_des_table').removeClass('d-none');
                    $(current_snippet).find('.document_des_not_avail').addClass('d-none');
                    
                    $(current_snippet).find('.display_name').html(data.display_name);
                    var html = ''
                    for (var i=0; i<data.product_documents_val.length; i++){
                        html += "<tr>"
                        html += '<td>'+data.product_documents_val[0].datas_fname+'</td>'
                        html += '<td>'+data.product_documents_val[0].product_description+'</td>'
                        html += '<td><a class="btn btn-success" href="/download-report/'+data.product_documents_val[0].id+'">Download</a></td>'    
                        html += "</tr>"
                    }
                    $(current_snippet).find('.inner_snippet_doc_row').html(html);
                    $(current_snippet).find('.modal_product_more_info').modal('show');
                } else {
                    $(current_snippet).find('.document_des_table').addClass('d-none');
                    $(current_snippet).find('.document_des_not_avail').removeClass('d-none');
                    $(current_snippet).find('.modal_product_more_info').modal('show');
                }
            });
        })
        // END CODE FOR MORE INFO BUTTON
    });
});
