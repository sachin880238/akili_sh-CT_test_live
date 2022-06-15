odoo.define('ct_web_checkout.ct_web_checkout', function (require) {
    "use strict";
    
var ajax = require('web.ajax');
$(document).ready(function(){
    $(".atttaa").click(function(){
        var attachment = $('#order_attachments.datas_fname').val()
    });
    $('#atttaa').on('click','#trash',function(){
        var self=this;
        var attachment_id=this.getElementsByTagName("input")[0];
        
        if (confirm('Do you want to remove this attachment?')) {
                ajax.jsonRpc('/delete_attachment/cart', 'call', {
                    attachment_id: attachment_id.value,
                    
                    }).then(function () {
                        $(self).parent().remove();
                        
                });}
        
    });

});


$(document).ready(function(){
    console.log("ASASASASASASASASAS")
    $(".trash1").click(function(){
        console.log("XXXX@!@#@#@@#@#")
        var self=this;
        var saved_cart_id=this.getElementsByTagName("input")[0];
        console.log("XXXXXX!!!!!!!!!!!",saved_cart_id)
        if (confirm('Do you want to remove this attachment?')) {
                ajax.jsonRpc('/delete_saved/cart', 'call', {
                    'saved_cart_id': saved_cart_id.value,
                    
                    }).then(function () {
                        
                        location.reload();
                        
                    });
                }
    });
    // $('#save_cart11').on('click','#trash1',function(){
    //     var self=this;
    //     var saved_cart_id=this.getElementsByTagName("input")[0];
    //     console.log("XXXXXX!!!!!!!!!!!",saved_cart_id)
    //     if (confirm('Do you want to remove this attachment?')) {
    //             ajax.jsonRpc('/delete_saved/cart', 'call', {
    //                 'saved_cart_id': saved_cart_id.value,
                    
    //                 }).then(function () {
    //                     $(self).parent().remove();
    //                     location.reload();
                        
    //                 });
    //             }
        
    // });

});



// var sAnimations = require('website.content.snippets.animation');

$( document ).ready(function() {

    $('.show-password').click(function(){
        if (($('#password').attr('type'))=='text'){
            $("#password").attr("type","password");
            this.innerText = 'Show'
        } else {
            $("#password").attr("type","text");
            this.innerText = 'Hide'
        }
    });

    $('.reset-password').click(function(){
        $("#password_check").val('')
    });

     if ($('input[type=radio][name=company_type]').val() == 'company'){
        $('#company_field').show();
        } else {
            $('#company_field').hide();
        }

    // CHANGE RADIO BUTTON COMPANY AND INDIVIDUAL
    $('input[type=radio][name=company_type]').change(function() {
        var input_tag = document.getElementById('page_content_new_account')
        if ($(this).val() == 'company'){
            input_tag.innerHTML="<b>Enter your company address and contact details.</b> We will use this to reference all of your addresses, documents, and communication, but you can specify adifferent billing address, shipping address, or contact person for each transaction. If you will purchasing as an individual, please set <i>Type</i> to“individual”.</p>"
            $('#company_field').show();
        } else {
            input_tag.innerHTML="<b>Enter your home address and contact details.</b>We will use this to reference all of your addresses, documents, and communication, but you can specify a different billing address, shipping address, or contact person for each transaction. If you will purchasing for a company, please set <i>Type</i> to “company”.</p>"
            $('#company_field').hide();
        }
    });

    $('#phone_number_test').click(function(){
        var phone = $('#telephone_number').val();
        ajax.jsonRpc("/check-number-is-valid", 'call', {
            'phone': phone
        }).then(function(data){
            if (data.valid == true){
                document.getElementById('messaget_valid').style.display='block';
                document.getElementById('phone_number_test').style.display='none';

                // console.log("IFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
                // // $('#messaget_not_valid').addClass("o_hidden");
                // var news = $('#messaget_valid').style.display;  
                // console.log("IFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", news)
            }
            else{
                console.log("essssssssssssssssssssssssssssssssssssssss")
                document.getElementById('messaget_not_valid').style.display='block';
                // $('#messaget_valid').addClass("o_hidden");
                // $('#messaget_not_valid').removeClass("o_hidden");
            }
        })
            
    });

    $('div.card_edit').on('click', '.js_edit_address', function(ev) {
        ev.preventDefault();
        $(ev.currentTarget).closest('div.one_kanban').find('form.d-none').attr('action', '/shop/address').submit();
    });

    $('.oe_cart').on('click', '.js_change_contact', function(ev) {
        if (!$('body.editor_enable').length) {

            var $old = $('.all_contact').find('.card.border_primary');
            $old.find('.btn-contact').toggle();
            $old.addClass('js_change_contact');
            $old.removeClass('border_primary');

            var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
            $new.find('.btn-contact').toggle();
            $new.removeClass('js_change_contact');
            $new.addClass('border_primary');

            var $form = $(ev.currentTarget).parent('div.one_kanban');
            var contact_address_id = $(this).find('a.js_delete_address').data('contact-id');
            $.post($form.find('form').attr('my/address-book'), $form.find('form').serialize()+'&contact_addres_id=' + contact_address_id);

        }
    });

    $('.oe_cart').on('click', '.js_change_billing', function(ev) {
        if (!$('body.editor_enable').length) { //allow to edit button text with editor
            var $old = $('.all_billing').find('.card.border_primary');
            $old.find('.btn-bill').toggle();
            $old.addClass('js_change_billing');
            $old.removeClass('border_primary');

            var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
            $new.find('.btn-bill').toggle();
            $new.removeClass('js_change_billing');
            $new.addClass('border_primary');

            var $form = $(ev.currentTarget).parent('div.one_kanban');
            var billing_address_id = $(this).find('a.js_delete_address').data('contact-id');
            $.post($form.find('form').attr('my/address-book'), $form.find('form').serialize()+'&billing_address_id=' + billing_address_id);

        }
    });

    $('.add_update_card').on('click', '.js_change_billing', function(ev) {
        if (!$('body.editor_enable').length) { //allow to edit button text with editor
            var $old = $('.all_billing').find('.card.border_primary');
            $old.find('.btn-bill').toggle();
            $old.addClass('js_change_billing');
            $old.removeClass('border_primary');

            var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
            $new.find('.btn-bill').toggle();
            $new.removeClass('js_change_billing');
            $new.addClass('border_primary');

            // var $form = $(ev.currentTarget).parent('div.one_kanban');
            var billing_address_id = $(this).data('contact-id');
        
            $("#billing_address_id").val(billing_address_id);
            // $.post($form.find('form').attr('my/address-book'), $form.find('form').serialize()+'&billing_address_id=' + billing_address_id);

        }
    });

    $('.oe_cart').on('click', '.js_change_shipping', function(ev) {
        if (!$('body.editor_enable').length) { //allow to edit button text with editor
            var $old = $('.all_shipping').find('.card.border_primary');
            $old.find('.btn-ship').toggle();
            $old.addClass('js_change_shipping');
            $old.removeClass('border_primary');

            var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
            $new.find('.btn-ship').toggle();
            $new.removeClass('js_change_shipping');
            $new.addClass('border_primary');

            var $form = $(ev.currentTarget).parent('div.one_kanban');
            var shipping_address_id = $(this).find('a.js_delete_address').data('contact-id');
            $.post($form.find('form').attr('my/address-book'), $form.find('form').serialize()+'&shipping_addres_id=' + shipping_address_id);
        }
    });

	$('.js_delete_address').on('click', function(e) {
        var $elem = $(this);
        var pid = parseInt($elem.attr('data-contact-id'));

        ajax.jsonRpc("/shop/partner/remove", 'call', {
            'partner_id': pid,
        }).then(function (data) {
            if (data && data.result){
                $elem.closest('div.one_kanban').remove();
            }
            else if(data && data.error_message) {
                $(`<div class="alert alert-danger">
                    `+ data.error_message.join('<br />') + `
                </div>`).prependTo('div.oe_cart');
            }
        });
    });

    // upload d0cument
	
    $('#order_attach_file').click(function(){
        $("#customer_priority_1").val(document.getElementById('customer_priority').value);
		$("#client_order_ref_1").val(document.getElementById('client_order_ref').value);
		$("#note_1").val(document.getElementById('note').value);
		$('#oe_upload_document').modal('show');
    });

	$(".modal").on("hidden.bs.modal", function(){
		$(".modal-body1").html("");
	});


    // START SAVE ORDER DETAIL ON ONCHANGE OF TEXT CONTENT
    $("form :input").change(function() {
        var customer_priority = $('#customer_priority').val();
        var client_order_ref = $('#client_order_ref').val();
        var note = $('#note').val();

        ajax.jsonRpc("/extra/save_order_detail", 'call', {
            'customer_priority': customer_priority,
            'client_order_ref': client_order_ref,
            'note': note
        }).then(function (data) {
        });
    });
    // END SAVE ORDER DETAIL ON ONCHANGE OF TEXT CONTENT

    $('#use_acc_comm').change(function() {
        if($(this).is(':checked')){
            ajax.jsonRpc("/get-contact-info", 'call').then(function (data) {
                if (data){
                    $('input[name="name"]').val(data.name);
                    $('input[name="comp_name"]').val(data.company);
                    $('input[name="street"]').val(data.street);
                    $('input[name="street2"]').val(data.street2);
                    $('input[name="city"]').val(data.city);
                    $('input[name="zip"]').val(data.zip);
                    $('input[name="email"]').val(data.email);
                    $('input[name="phone"]').val(data.phone);
                    $('input[name="alternate_communication_1"]').val(data.other_communication_1);
                    $('input[name="alternate_communication_2"]').val(data.other_communication_2);

                    $('select[name="state_id"]').val(data.state_id);
                    $('select[name="country_id"]').val(data.country_id);
                    $('select[name="primary_tel_type"]').val(data.primary_tel_type);
                    $('select[name="alternate_commu_type_1"]').val(data.other_communication_type_1);
                    $('select[name="alternate_commu_type_2"]').val(data.other_communication_type_2);
                }
            });
        }

        if($(this).is(':checked') == false){
            $('input[name="name"]').val('');
            $('input[name="comp_name"]').val('');
            $('input[name="street"]').val('');
            $('input[name="street2"]').val('');
            $('input[name="city"]').val('');
            $('input[name="zip"]').val('');
            $('input[name="email"]').val('');
            $('input[name="phone"]').val('');
            $('input[name="alternate_communication_1"]').val('');
            $('input[name="alternate_communication_2"]').val('');

            $('select[name="state_id"]').val('');
            $('select[name="country_id"]').val('');
            $('select[name="primary_tel_type"]').val('');
            $('select[name="alternate_commu_type_1"]').val('');
            $('select[name="alternate_commu_type_2"]').val('');
        }

    });
    

    $('.accessory_plus_quantity').click(function(){
        var input_tag = document.getElementsByClassName('product-action-div-snippet')
        var product_inc=$(this).prev("span")
        var span_quatity=$(input_tag[0]).find('.qty_product');
        var now_quantity=parseInt(product_inc[0].innerHTML)+1
        product_inc.html(now_quantity)
        var td_tag=product_inc[0].parentElement;
        var a_tag=td_tag.parentElement;
        var next_td=a_tag.nextElementSibling
        var pro_unit_price=next_td.getElementsByTagName("span");
        var pro_unit_price1=pro_unit_price[0].getElementsByClassName("oe_currency_value");
        var net_price = (now_quantity) * (pro_unit_price1[0]).innerHTML

        var final_td=next_td.nextElementSibling
        var span=final_td.getElementsByClassName("oe_currency_value");
        span[0].innerHTML = parseFloat(net_price).toFixed(2)

    });


    $('.accessory_minus_quantity').click(function(){
        var input_tag = document.getElementsByClassName('product-action-div-snippet')
        var product_dec=$(this).next("span")
        var span_quatity=$(input_tag[0]).find('.qty_product');
        if(parseInt(span_quatity[0].innerHTML) != 0){
            var now_quantity=parseInt(product_dec[0].innerHTML)-1
            if (now_quantity>0){
                product_dec.html(now_quantity)
            }
            // product_dec.html(now_quantity)

            var td_tag=product_dec[0].parentElement;
            var a_tag=td_tag.parentElement;
            var next_td=a_tag.nextElementSibling
            var pro_unit_price=next_td.getElementsByTagName("span");
            var pro_unit_price1=pro_unit_price[0].getElementsByClassName("oe_currency_value");
            var net_price = (now_quantity) * (pro_unit_price1[0]).innerHTML

            var final_td=next_td.nextElementSibling
            var span=final_td.getElementsByClassName("oe_currency_value");
            if (net_price>0){
                span[0].innerHTML = parseFloat(net_price).toFixed(2)
            }
            
        }
    });


    $('.custom_add_to_cart_accessory_product').click(function(){
        var custom_add_to_cart_product = document.getElementsByClassName('product-action-div-snippet')
        var product_id=$(custom_add_to_cart_product).find('.sugested_products')[0].value
        var product_id1=$(this).prev("input")
        var quantity=$(custom_add_to_cart_product).find('.qty_product')[0].innerHTML
        ajax.jsonRpc("/shop/cart/update_json", 'call', {
            'product_id': parseInt(product_id1[0].value),
            'add_qty': parseInt(quantity) || 1 ,
         });
    });    

});

});

function submit_form() {
  $('#oe_upload_document').modal('hide');
  setTimeout(location.reload.bind(location), 1000);

}


