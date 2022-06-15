odoo.define('website_product_detail_page.product', function (require) {
    "use strict";

    var base = require('web_editor.base'),
        ajax = require('web.ajax'),
        core = require('web.core'),
        utils = require('web.utils'),
        _t = core._t,
        sAnimations = require('website.content.snippets.animation');
    // var website_sale = require('website_sale.website_sale.website_sale')    
    var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');          
    var config = require('web.config')

    // Start change product decription base on variant    
    sAnimations.registry.WebsiteSale.include({
    	read_events: {
	        'change form .js_product:first input[name="add_qty"]': '_onChangeAddQuantity',
	        'mouseup .js_publish': '_onMouseupPublish',
	        'touchend .js_publish': '_onMouseupPublish',
	        'change .oe_cart input.js_quantity[data-product-id]': '_onChangeCartQuantity',
	        'click .oe_cart a.js_add_suggested_products': '_onClickSuggestedProduct',
	        'click a.js_add_cart_json': '_onClickAddCartJSON',
	        'click .a-submit': '_onClickSubmit',
	        'change form.js_attributes input, form.js_attributes select': '_onChangeAttribute',
	        'mouseup form.js_add_cart_json label': '_onMouseupAddCartLabel',
	        'touchend form.js_add_cart_json label': '_onMouseupAddCartLabel',
	        'change .css_attribute_color input': '_onChangeColorAttribute',
	        'click .show_coupon': '_onClickShowCoupon',
	        'submit .o_website_sale_search': '_onSubmitSaleSearch',
	        'change select[name="country_id"]': '_onChangeCountry',
	        'change #shipping_use_same': '_onChangeShippingUseSame',
	        'click .toggle_summary': '_onToggleSummary',
	        'click input.js_product_change': 'onChangeVariant',
	        // dirty fix: prevent options modal events to be triggered and bubbled
	        'change oe_optional_products_modal [data-attribute_exclusions]': 'onChangeVariant',
	        'change select.js_variant_selection_change': '_OnVariantSelectionChange',
            'change input.js_variant_change':'attribute_selection_data_change',
            'change select.js_variant_change':'attribute_selection_data_change',
    	},
        
        _onChangeCombination: function (ev, $parent, combination) {
            this._super.apply(this, arguments);
            if(combination.product_id){
                $('.variant_description_div').addClass("d-none");
                $('#variant_description_div_'+combination.product_id).removeClass('d-none');
                $('.add_to_cart_process').removeClass("d-none");
                $('.variant_description_main_div').addClass("d-none");
                $('.template_description_main_div').addClass("d-none");
                $('#variant_description_main_div_'+combination.product_id).removeClass('d-none');

            }
        },


        _OnVariantSelectionChange: function (ev) {
            var self = this;
            ev.preventDefault();
            var $variantValueInput = $(ev.currentTarget);
            if ($variantValueInput.is('select')){
                $variantValueInput = $variantValueInput.find('option[value=' + $variantValueInput.val() + ']');
            }
            var $component;
            if ($(ev.currentTarget).closest('form').length > 0){
                $component = $(ev.currentTarget).closest('form');
            } else if ($(ev.currentTarget).closest('.oe_optional_products_modal').length > 0){
                $component = $(ev.currentTarget).closest('.oe_optional_products_modal');
            } else if ($(ev.currentTarget).closest('.o_product_configurator').length > 0) {
                $component = $(ev.currentTarget).closest('.o_product_configurator');
            } else {
                $component = $(ev.currentTarget);
            }
            var qty = $component.find('input[name="add_qty"]').val();
            var $parent = $(ev.target).closest('.js_product');
            var combination = $variantValueInput.data('attribute_value_ids');
            var product_template_id = $variantValueInput.data('product_tmpl_id')
            var product_id = parseInt($variantValueInput.val())|| 0
            var rootComponentSelectors = [
                'tr.js_product',
                '.oe_website_sale',
                '.o_product_configurator'
            ];
            if(product_id > 0){
                ajax.jsonRpc('/product_configurator/get_combination_info_website', 'call', {
                    product_template_id: product_template_id,
                    product_id: product_id,
                    combination: combination,
                    add_qty: parseInt(qty),
                    pricelist_id: this.pricelistId || false,
                    }).then(function (combinationData) {
                        console.log("QQQQQQQQQQQQQQQQQQQ",combinationData)
                        console.log("EEEEEEEEEEEEEEEEEEE",self.$el[0])
                        var document_view=self.$el[0].getElementsByClassName("document_button");
                        console.log("-==-==%%%%%%%%%%%%%%%%%%%%%%%%%%",document_view)
                        if(combinationData.document == true){
                            document_view[0].style.opacity=1
                            document_view[0].style.pointerEvents = "all";
                        }
                        else{
                            document_view[0].style.opacity=0.5
                            document_view[0].style.pointerEvents = "none";

                        }
                        
                        self._onChangeCombination(ev, $parent, combinationData);
                        var product_name=document.getElementsByClassName("row col-md-12")[2]
                        var container=product_name.getElementsByClassName('container')
                        for(var i=0;i<container.length;i++){
                            var product_real_name_tag=container[i].getElementsByClassName('variant_description_div')[0]
                            var product_id="variant_description_div_"+combinationData.product_id.toString();
                            if(product_real_name_tag.id==product_id){
                                product_real_name_tag.classList.remove("d-none");
                                
                            }                // if(product_real_name_tag.id==)
                            else{
                                product_real_name_tag.classList.add("d-none");
                                
                            }
                        }
                         var button=document.getElementById("add_to_cart_custom")
                         button.style.opacity=1   
                        button.style.pointerEvents = "";
                        $( '.add_to_cart_process' ).removeClass( "d-none" )
                });

            }else{
            	self.last_product_id = false
                ajax.jsonRpc('/website_product_detail_page/get_update_product_image', 'call', {
                    product_template_id: product_template_id,
                    pricelist_id: this.pricelistId || false,
                    product_id: product_id,
                    }).then(function (combinationData) {
                        self._updateProductImage(
                            $parent.closest(rootComponentSelectors.join(', ')),
                            combinationData.product_id,
                            combinationData.product_template_id,
                            combinationData.carousel
                        );
                        
                });

                $('.add_to_cart_process').addClass("d-none");
                $('.variant_description_div').addClass("d-none");
                $('.variant_description_main_div').addClass("d-none");
                $('.template_description_main_div').removeClass("d-none");    
            }     
        }, 
         _onChangeCombination: function (ev, $parent, combination) {
        var self = this;
        var $price = $parent.find(".oe_price:first .oe_currency_value");
        var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
        var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");

        var isCombinationPossible = this.isSelectedVariantAllowed;

        if (combination.is_combination_possible !== undefined) {
            isCombinationPossible = combination.is_combination_possible;
        }

        this._toggleDisable($parent, isCombinationPossible);
        if (combination.uom_id !== undefined) {
            $price.html(self._priceToStr(combination.price)+"/"+combination.uom_id);
            $default_price.html(self._priceToStr(combination.list_price));
        }
        else{
           $price.html(self._priceToStr(combination.price));
           $default_price.html(self._priceToStr(combination.list_price));
        }

        // $price.html(self._priceToStr(combination.price)+"/"+combination.uom_id);
        // $default_price.html(self._priceToStr(combination.list_price));

        // compatibility_check to remove in master
        // needed for fix in 12.0 in the case of git pull and no server restart
        var compatibility_check = combination.list_price - combination.price >= 0.01;
        if (combination.has_discounted_price !== undefined ? combination.has_discounted_price : compatibility_check) {
            $default_price
                .closest('.oe_website_sale')
                .addClass("discount");
            $optional_price
                .closest('.oe_optional')
                .removeClass('d-none')
                .css('text-decoration', 'line-through');
            $default_price.parent().removeClass('d-none');
        } else {
            $default_price
                .closest('.oe_website_sale')
                .removeClass("discount");
            $optional_price.closest('.oe_optional').addClass('d-none');
            $default_price.parent().addClass('d-none');
        }

        var rootComponentSelectors = [
            'tr.js_product',
            '.oe_website_sale',
            '.o_product_configurator'
        ];

        // update images only when changing product
        if (combination.product_id !== this.last_product_id) {
            this.last_product_id = combination.product_id;
            self._updateProductImage(
                $parent.closest(rootComponentSelectors.join(', ')),
                combination.product_id,
                combination.product_template_id,
                combination.carousel,
                isCombinationPossible
            );
            
        }
        if (combination.product_id == this.last_product_id) {
            this.last_product_id = combination.product_id;
            self._updateProductImage(
                $parent.closest(rootComponentSelectors.join(', ')),
                combination.product_id,
                combination.product_template_id,
                combination.carousel,
                isCombinationPossible
            );
            
        }

        $parent
            .find('.product_id')
            .first()
            .val(combination.product_id || 0)
            .trigger('change');

        $parent
            .find('.product_display_name')
            .first()
            .val(combination.display_name);

        $parent
            .find('.js_raw_price')
            .first()
            .html(combination.price);

        this.handleCustomValues($(ev.target));
    },
        attribute_selection_data_change: function (ev) {
        var $parent = $(ev.target).closest('.js_product');
        if (!$parent.data('uniqueId')) {
            $parent.data('uniqueId', _.uniqueId());
        }
        this._throttledGetCombinationInfo($parent.data('uniqueId'))(ev);
            
        },
        _getCombinationInfo: function (ev) {
        var self = this;

        var $component;
        if ($(ev.currentTarget).closest('form').length > 0){
            $component = $(ev.currentTarget).closest('form');
        } else if ($(ev.currentTarget).closest('.oe_optional_products_modal').length > 0){
            $component = $(ev.currentTarget).closest('.oe_optional_products_modal');
        } else if ($(ev.currentTarget).closest('.o_product_configurator').length > 0) {
            $component = $(ev.currentTarget).closest('.o_product_configurator');
        } else {
            $component = $(ev.currentTarget);
        }
        var qty = $component.find('input[name="add_qty"]').val();

        var $parent = $(ev.target).closest('.js_product');

        var combination = this.getSelectedVariantValues($parent);
        var parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;

        var productTemplateId = parseInt($parent.find('.product_template_id').val());

        self._checkExclusions($parent, combination);
        return ajax.jsonRpc(this._getUri('/product_configurator/get_combination_info'), 'call', {
            'product_template_id': productTemplateId,
            'product_id': this._getProductId($parent),
            'combination': combination,
            'add_qty': parseInt(qty),
            'selector':ev.currentTarget.value,
            'seleted_attribute':ev.currentTarget.dataset.attribute_id,
            'pricelist_id': this.pricelistId || false,
            'parent_combination': parentCombination,
        }).then(function (combinationData) {
            
            var temp_check=0
            console.log("QQQQQQQQQQQQQQQQQQQ",self,combinationData)
            console.log("EEEEEEEEEEEEEEEEEEE",self.$el[0])
            var document_view=self.$el[0].getElementsByClassName("document_button");
            console.log("-==-==%%%%%%%%%%%%%%%%%%%%%%%%%%",document_view)
            if(combinationData.document == true){
                document_view[0].style.opacity=1
                document_view[0].style.pointerEvents = "all";
            }
            else{
                document_view[0].style.opacity=0.5
                document_view[0].style.pointerEvents = "none";

            }
            if(ev.currentTarget.type=='select-one'){
                if(ev.currentTarget.value != 'none'){
                    for(var j=0;j<Object.keys(combinationData.final_dict).length;j++){
                        var select_field_name='attribute-'+combinationData.product_template_id+"-"+Object.keys(combinationData.final_dict)[j];
                        
                        var x = document.getElementsByName(select_field_name);
                        x[0].options.length=1
                        console.log("fffffffffffffffffffffffff",x[0].options)
                        for(var k=0;k<combinationData.final_dict[Object.keys(combinationData.final_dict)[j]].length;k++){
                            var option =document.createElement("option");
                            option.text = combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][k][1]+" "+combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][k][2];
                            option.value=combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][k][0];
                            x[0].add(option);
                            
                        }
                        console.log(combinationData.combination[Object.keys(combinationData.final_dict)[j]-1])
                        // if(combinationData.combination[Object.keys(combinationData.final_dict)[j]-1]!=null){
                        //     console.log("------------------",combinationData.combination,Object.keys(combinationData.final_dict),combinationData.combination,combinationData.combination[Object.keys(combinationData.final_dict)[j]-1])
                        //     x[0].value=combinationData.combination[j]
                        // }
                    }
                   
                    for(var temp=0;temp<=combinationData.combination.length;temp++){
                        if(combinationData.combination[temp]!=null){
                            var select_field_name='attribute-'+combinationData.product_template_id+"-"+temp;
                            var x = document.getElementsByClassName("js_variant_change");
                            x[temp].value=combinationData.combination[temp]
                            if(x[temp].value.length==0){
                                x[temp].value='none'
                                temp_check=temp_check+1
                            }

                        }

                    }
                    if(temp_check!=0){
                        var rootComponentSelectors = [
                            'tr.js_product',
                            '.oe_website_sale',
                            '.o_product_configurator'
                        ];
                        self._updateProductImage(
                            $parent.closest(rootComponentSelectors.join(', ')),
                            combinationData.product_id,
                            combinationData.product_template_id,
                            combinationData.carousel
                        );
                        
                        $('.add_to_cart_process').addClass("d-none");
                        $('.custom_product_name').addClass("d-none");

                    }
                }
                else{
                    ev.currentTarget.options.length=1
                    for(var i=0;i<combinationData.temp.length;i++){
                        var option =document.createElement("option");
                        option.text = combinationData.temp[i][1]
                        option.value=combinationData.temp[i][0];
                        ev.currentTarget.add(option);

                    }

                }}
            // if(ev.currentTarget.type=='radio'){
            //     for(var j=0;j<Object.keys(combinationData.final_dict).length;j++){
            //         var x = document.getElementsByClassName("js_attribute_value");
            //         for(var k=0;k<x.length;k++){
            //             var final_temp=0
            //             var input= x[k].getElementsByTagName('input');
            //             if(Object.keys(combinationData.final_dict)[j]==input[0].dataset.attribute_id){
            //                 var temp=0
            //                 for(var check_field=0;check_field<combinationData.final_dict[Object.keys(combinationData.final_dict)[j]].length;check_field++){
            //                     if(combinationData.final_dict[Object.keys(combinationData.final_dict)[j]][check_field][0]==input[0].value){
            //                         x[k].style.display='block'
            //                         temp=temp+1
            //                         final_temp=final_temp+1
            //                     }
                                
            //                 }
            //                 if(temp==0){

            //                         x[k].style.display='none'
            //                         var parent=x[k].parentElement
            //                         // parent.style.display='none'

                                
            //                 }
            //             }
                        
            //             // if(final_temp==0){
            //             //     console.log("-----------------finaltemp")
            //             //     var parent=x[k].parentElement
            //             //     console.log("--------------------------------parent",parent)
            //             //     parent.style.display='none'
            //             // }
            //             // else{
            //             //     var parent=x[k].parentElement
            //             //     console.log("--------------------------------parent",parent)
            //             //     parent.style.display='block'

            //             // }

                        
            //         }

            //     }
            //     if(ev.currentTarget.value){
            //                 var temp=0
            //                  var x = document.getElementsByClassName("js_attribute_value");
            //                 for(var check_field=0;check_field<x.length;check_field++){
            //                     var parent=x[check_field].parentElement
            //                     if(parent.dataset.attribute_id==ev.currentTarget.dataset.attribute_id){
            //                         x[check_field].style.display="block"

            //                     }
                                
            //                         // x[k].style.display='block'
            //                         // temp=temp+1
            //                         // final_temp=final_temp+1
                                
                                
            //                 }

            //             }

                
            // }

            var product_name=document.getElementsByClassName("row col-md-12")[1]
            var container=product_name.getElementsByClassName('container')
            for(var i=0;i<container.length;i++){
                var product_real_name_tag=container[i].getElementsByClassName('variant_description_div')[0]
                var product_id="variant_description_div_"+combinationData.product_id.toString();
                if(product_real_name_tag.id==product_id){
                    product_real_name_tag.classList.remove("d-none");
                    
                }                // if(product_real_name_tag.id==)
                else{
                    product_real_name_tag.classList.add("d-none");
                    
                }
            }
            if (temp_check==0){
            // $('#variant_description_div_15').addClass("d-none");
            if(combinationData.publish==true){
                self._onChangeCombination(ev, $parent, combinationData);

                var button=document.getElementById("add_to_cart_custom")
                var image = document.getElementsByClassName("carousel-item")[0];
                var image_data = document.getElementsByClassName("product_detail_img")[0];
                var node = document.createElement("div");
                  var textnode = document.createTextNode("Out Of Stock");
                  node.setAttribute('class', 'text-block fade_text_block');
                  node.appendChild(textnode);

                  image.appendChild(node);
                image_data.style.opacity=1
                image_data.style.pointerEvents = "all";
                button.style.opacity=1   
                button.style.pointerEvents = "all";
                $( '.add_to_cart_process' ).removeClass( "d-none" )
                $( '.custom_product_name' ).removeClass( "d-none" )
            }
            else{
                try {
                        self._onChangeCombination(ev, $parent, combinationData);  
                        var button=document.getElementById("add_to_cart_custom")
                        button.style.opacity=0.5
                        button.style.pointerEvents = "none";
                        var image = document.getElementsByClassName("carousel-item")[0];
                        var image_data = document.getElementsByClassName("product_detail_img")[0];
                        var node = document.createElement("div");
                          var textnode = document.createTextNode("Out Of Stock");
                          node.setAttribute('class', 'text-block');
                          node.appendChild(textnode);

                          image.appendChild(node);
                        image_data.style.opacity=0.2
                        image_data.style.pointerEvents = "none";
                        $( '.add_to_cart_process' ).removeClass( "d-none" )
                        $( '.custom_product_name' ).removeClass( "d-none" )
                    }
                    catch(err) {
                        var rootComponentSelectors = [
                            'tr.js_product',
                            '.oe_website_sale',
                            '.o_product_configurator'
                        ];
                        self._updateProductImage(
                            $parent.closest(rootComponentSelectors.join(', ')),
                            combinationData.product_id,
                            combinationData.product_template_id,
                            combinationData.carousel
                        );
                        
                        $('.add_to_cart_process').addClass("d-none");
                        $('.custom_product_name').addClass("d-none");
                    }
                
                
            }}
            
        });
    },



        _startZoom: function () {
        // Do not activate image zoom for mobile devices, since it might prevent users from scrolling the page
            if (!config.device.isMobile) {
                var autoZoom = $('.ecom-zoomable').data('ecom-zoom-auto') || false,
                factorZoom = parseFloat($('.ecom-zoomable').data('ecom-zoom-factor')) || 1.5,
                attach = '#o-carousel-product';
                _.each($('.ecom-zoomable img[data-zoom]'), function (el) {
                    onImageLoaded(el, function () {
                        var $img = $(el);
                        $img.attr('data-imagezoom', 'true');
                        $img.attr('data-zoomviewsize','[400,500]');
                    });
                });
            }

            function onImageLoaded(img, callback) {
                // On Chrome the load event already happened at this point so we
                // have to rely on complete. On Firefox it seems that the event is
                // always triggered after this so we can rely on it.
                //
                // However on the "complete" case we still want to keep listening to
                // the event because if the image is changed later (eg. product
                // configurator) a new load event will be triggered (both browsers).
                $(img).on('load', function () {
                    callback();
                });
                if (img.complete) {
                    callback();
                }
            }
        },

    });
  
 
    $( document ).ready(function() {
        // START ON ADD TO CART POPOVER INPLACE OF REDIRECTING CART
       $('.custom_add_to_cart').off('click').on('click', function (event) {
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
        
        // END ON ADD TO CART POPOVER INPLACE OF REDIRECTING CART

        //START JS FOR MORE INFO (DOCUMENTS)
        $('#product_more_info').on("click", function(e){
            var $form = $(this).closest('form');
            var product_id = $form.find('.product_id').val() || $form.find('input[name="product_id"]:first').val()
            var modal_id = "#product_more_info_modal_"+product_id
            $(modal_id).modal("show");
        });
        //END JS FOR MORE INFO (DOCUMENTS)

    });
});

function check_product_bindle(x){
    var product = document.getElementById("product_select");
    var product2 = $('.quantity').val(1)
    $.ajax({
            url: "/check/product/variants/",
            method: "POST",
            dataType: "json",
            data: { product_id: x

            },
            success: function( data ) {
            if(data.count>0){
                document.getElementById("hidden_for_type_input_field").value=parseInt(data.check_no_of_bombs_ids)

            }
            else{
                document.getElementById("hidden_for_type_input_field").value=0
            }
        }
    });

}
function add_quantity(argument) {
    var input_max = argument.getElementsByTagName('input')[0]
    argument.previousElementSibling.value=parseInt(argument.previousElementSibling.value)+1
    var input_min = argument.getElementsByTagName('input')[1]
    var max_quantity = argument.parentElement.parentElement.getElementsByClassName("max_quantity_bomb")[0]
    var count_line_bundle= argument.parentElement.parentElement.getElementsByClassName('bundel_line_count')[0]
    
    if(max_quantity.value != ''){
        qty_bom_total=0
        for(var i=0;i<parseInt(count_line_bundle.value);i++){
                    var qty_bom = argument.parentElement.parentElement.getElementsByClassName("add_qty_bomb")[i].value;
                    qty_bom_total=qty_bom_total+parseInt(qty_bom)
                    
                }
        if(parseInt(max_quantity.value) <= qty_bom_total){
           for(var i=0;i<parseInt(count_line_bundle.value);i++){
                    var plus_button = argument.parentElement.parentElement.getElementsByClassName("plus_button")[i];
                    plus_button.style.opacity=0.5
                    plus_button.style.pointerEvents = "none";
                    var min_qty = argument.parentElement.parentElement.getElementsByClassName("min_quantity")[i]
                    var qty_input = argument.parentElement.parentElement.getElementsByClassName("add_qty_bomb")[i]
                    if(parseInt(min_qty.value) == parseInt(qty_input.value)){
                        var plus_button = argument.parentElement.parentElement.getElementsByClassName("minus_button")[i];
                        plus_button.style.opacity=0.5
                        plus_button.style.pointerEvents = "none";
                    }
                    else{
                        var plus_button = argument.parentElement.parentElement.getElementsByClassName("minus_button")[i];
                        plus_button.style.opacity=1
                        plus_button.style.pointerEvents = "all";

                    }
                    
                }


        }
        else{
            if(parseInt(argument.previousElementSibling.value) == parseInt(input_max.value)){
            argument.style.opacity=0.5
            argument.style.pointerEvents = "none";
        }
        if(parseInt(argument.previousElementSibling.value) >= parseInt(input_min.value)){
            var minus_button=argument.previousElementSibling.previousElementSibling
            minus_button.style.opacity=1
            minus_button.style.pointerEvents='all'
            minus_button.style.pointer="cursor"
            
        }

        }

        
    }
    else{
            if(parseInt(argument.previousElementSibling.value) == parseInt(input_max.value)){
            argument.style.opacity=0.5
            argument.style.pointerEvents = "none";
        }
        if(parseInt(argument.previousElementSibling.value) >= parseInt(input_min.value)){
            var minus_button=argument.previousElementSibling.previousElementSibling
            minus_button.style.opacity=1
            minus_button.style.pointerEvents='all'
            minus_button.style.pointer="cursor"
            
        }

        }


        


    // body...
}
function minus_quantity(argument) {
    var input_max = argument.getElementsByTagName('input')[0]
    var input_min = argument.getElementsByTagName('input')[1]
    argument.nextElementSibling.value=parseInt(argument.nextElementSibling.value)-1
    var max_quantity = argument.parentElement.parentElement.getElementsByClassName("max_quantity_bomb")[0]
    var count_line_bundle= argument.parentElement.parentElement.getElementsByClassName('bundel_line_count')[0]
    
    if(max_quantity.value != ''){
        qty_bom_total=0
        for(var i=0;i<parseInt(count_line_bundle.value);i++){
                    var qty_bom = argument.parentElement.parentElement.getElementsByClassName("add_qty_bomb")[i].value;
                    qty_bom_total=qty_bom_total+parseInt(qty_bom)
                    
                }
        
            if(parseInt(argument.nextElementSibling.value) < parseInt(input_max.value)){
                for(var i=0;i<parseInt(count_line_bundle.value);i++){
                    var minus_button=argument.parentElement.parentElement.getElementsByClassName("plus_button")[i];
                    var max_qty = argument.parentElement.parentElement.getElementsByClassName("max_quantity")[i].value
                    var qty_bom = argument.parentElement.parentElement.getElementsByClassName("add_qty_bomb")[i].value;
                    if (parseInt(max_qty) >  parseInt(qty_bom)){

                    minus_button.style.opacity=1
                    minus_button.style.pointerEvents='all'
                    }
                }
            
            
        }
        if(parseInt(argument.nextElementSibling.value) == parseInt(input_min.value)){
            argument.style.opacity=0.5
            argument.style.pointerEvents = "none";
            minus_button.style.pointer="none"
            
        }
    

    }
    else{
            if(parseInt(argument.nextElementSibling.value) < parseInt(input_max.value)){
        var minus_button=argument.nextElementSibling.nextElementSibling
        argument.nextElementSibling.nextElementSibling.style.opacity=1
        argument.nextElementSibling.nextElementSibling.style.pointerEvents='all'
        
    }
    if(parseInt(argument.nextElementSibling.value) == parseInt(input_min.value)){
        argument.style.opacity=0.5
        argument.style.pointerEvents = "none";
        minus_button.style.pointer="none"
        
    }

    }
    

    
   
}
