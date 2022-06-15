odoo.define('custom_web_checkout.update', function (require) {
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
    	},

         _onMouseupAddCartLabel: function (ev) { // change price when they are variants
           console.log("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
            var $label = $(ev.currentTarget);
            console.log("ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")
            var $price = $label.parents("form:first").find(".oe_price .oe_currency_value");
            if (!$price.data("price")) {
                $price.data("price", parseFloat($price.text()));
            }
            console.log("dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
            var value = $price.data("price") + parseFloat($label.find(".badge span").text() || 0);

            var dec = value % 1;
            $price.html(value + (dec < 0.01 ? ".00" : (dec < 1 ? "0" : "") ));
        },
        
        _onClickAddCartJSON: function (ev){
            console.log("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
            this.onClickAddCartJSON(ev);
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
                        self._onChangeCombination(ev, $parent, combinationData);
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